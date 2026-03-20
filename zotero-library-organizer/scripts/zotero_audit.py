#!/usr/bin/env python3
import argparse
import hashlib
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


DEFAULT_DB = Path(os.environ.get("ZOTERO_DB_PATH", str(Path.home() / "Zotero" / "zotero.sqlite")))


def snapshot_db(db_path: Path):
    temp_dir = Path(tempfile.mkdtemp(prefix="zotero-audit-"))
    snapshot = temp_dir / db_path.name
    shutil.copy2(db_path, snapshot)
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(db_path) + suffix)
        if sidecar.exists():
            shutil.copy2(sidecar, temp_dir / sidecar.name)
    return snapshot, temp_dir


def connect_readable(db_path: Path):
    snapshot, temp_dir = snapshot_db(db_path)
    conn = sqlite3.connect(str(snapshot))
    return conn, temp_dir


def field_ids(cur):
    return {name: fid for fid, name in cur.execute("SELECT fieldID, fieldName FROM fields")}


def get_field(cur, item_id, fid):
    if not fid:
        return ""
    row = cur.execute(
        """
        SELECT v.value
        FROM itemData d
        JOIN itemDataValues v ON v.valueID = d.valueID
        WHERE d.itemID=? AND d.fieldID=?
        """,
        (item_id, fid),
    ).fetchone()
    return row[0] if row else ""


def norm_title(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text


def norm_doi(text: str) -> str:
    text = (text or "").strip().lower()
    text = text.replace("https://doi.org/", "").replace("http://doi.org/", "").replace("doi:", "")
    return text


def parent_items(cur):
    return cur.execute(
        """
        SELECT i.itemID, i.key, it.typeName
        FROM items i
        JOIN itemTypes it ON it.itemTypeID=i.itemTypeID
        LEFT JOIN deletedItems di ON di.itemID=i.itemID
        WHERE di.itemID IS NULL
        AND i.itemID NOT IN (SELECT itemID FROM itemAttachments)
        AND i.itemID NOT IN (SELECT itemID FROM itemNotes)
        AND i.itemID NOT IN (SELECT itemID FROM itemAnnotations)
        """
    ).fetchall()


def collection_path_lookup(cur):
    rows = cur.execute("SELECT collectionID, collectionName, parentCollectionID FROM collections").fetchall()
    by_id = {cid: (name, parent) for cid, name, parent in rows}

    def path(cid):
        names = []
        while cid is not None:
            name, parent = by_id[cid]
            names.append(name)
            cid = parent
        return " / ".join(reversed(names))

    return rows, path


def cmd_summary(cur):
    rows, path = collection_path_lookup(cur)
    top = [(cid, name) for cid, name, parent in rows if parent is None]
    print("TOP_LEVEL_COLLECTIONS")
    for cid, name in sorted(top, key=lambda x: x[1].lower()):
        cnt = cur.execute(
            """
            SELECT COUNT(*)
            FROM collectionItems ci
            JOIN items i ON i.itemID=ci.itemID
            LEFT JOIN deletedItems di ON di.itemID=i.itemID
            WHERE ci.collectionID=? AND di.itemID IS NULL
            """,
            (cid,),
        ).fetchone()[0]
        print(f"{name}\t{cnt}")
        children = cur.execute(
            "SELECT collectionID, collectionName FROM collections WHERE parentCollectionID=? ORDER BY collectionName COLLATE NOCASE",
            (cid,),
        ).fetchall()
        for child_id, child_name in children:
            ccnt = cur.execute(
                """
                SELECT COUNT(*)
                FROM collectionItems ci
                JOIN items i ON i.itemID=ci.itemID
                LEFT JOIN deletedItems di ON di.itemID=i.itemID
                WHERE ci.collectionID=? AND di.itemID IS NULL
                """,
                (child_id,),
            ).fetchone()[0]
            print(f"  - {child_name}\t{ccnt}")


def cmd_unfiled(cur):
    fids = field_ids(cur)
    top_level = cur.execute(
        """
        SELECT i.itemID, i.key, it.typeName
        FROM items i
        JOIN itemTypes it ON it.itemTypeID=i.itemTypeID
        LEFT JOIN deletedItems di ON di.itemID=i.itemID
        WHERE di.itemID IS NULL
        AND i.itemID NOT IN (SELECT itemID FROM itemAttachments)
        AND i.itemID NOT IN (SELECT itemID FROM itemNotes)
        AND i.itemID NOT IN (SELECT itemID FROM itemAnnotations)
        AND NOT EXISTS (SELECT 1 FROM collectionItems ci WHERE ci.itemID=i.itemID)
        ORDER BY i.itemID
        """
    ).fetchall()
    print("TOP_LEVEL_UNFILED", len(top_level))
    for item_id, key, typ in top_level:
        title = get_field(cur, item_id, fids.get("title"))
        print(f"{key}\t{typ}\t{title}")

    standalone_attachments = cur.execute(
        """
        SELECT i.itemID, i.key, it.typeName
        FROM items i
        JOIN itemTypes it ON it.itemTypeID=i.itemTypeID
        JOIN itemAttachments ia ON ia.itemID=i.itemID
        LEFT JOIN deletedItems di ON di.itemID=i.itemID
        WHERE di.itemID IS NULL
        AND ia.parentItemID IS NULL
        AND NOT EXISTS (SELECT 1 FROM collectionItems ci WHERE ci.itemID=i.itemID)
        ORDER BY i.itemID
        """
    ).fetchall()
    print("STANDALONE_ATTACHMENT_UNFILED", len(standalone_attachments))
    for item_id, key, typ in standalone_attachments:
        title = get_field(cur, item_id, fids.get("title"))
        print(f"{key}\t{typ}\t{title}")


def cmd_duplicates(cur, storage_root: Path):
    fids = field_ids(cur)
    items = []
    for item_id, key, typ in parent_items(cur):
        title = get_field(cur, item_id, fids.get("title"))
        doi = get_field(cur, item_id, fids.get("DOI"))
        cols = cur.execute(
            """
            SELECT c.collectionName
            FROM collections c
            JOIN collectionItems ci ON c.collectionID=ci.collectionID
            WHERE ci.itemID=?
            ORDER BY c.collectionName COLLATE NOCASE
            """,
            (item_id,),
        ).fetchall()
        items.append(
            {
                "itemID": item_id,
                "key": key,
                "type": typ,
                "title": title,
                "doi": doi,
                "collections": [c[0] for c in cols],
            }
        )

    by_doi = defaultdict(list)
    by_title = defaultdict(list)
    for item in items:
        nd = norm_doi(item["doi"])
        nt = norm_title(item["title"])
        if nd:
            by_doi[nd].append(item)
        if nt:
            by_title[nt].append(item)

    print("DUPLICATE_DOI_GROUPS")
    for doi, group in sorted(by_doi.items()):
        if len(group) > 1:
            print("---")
            print(doi)
            for item in group:
                cols = " ; ".join(item["collections"]) if item["collections"] else "[no collection]"
                print(f"{item['key']}\t{item['type']}\t{item['title']}\t{cols}")

    print("DUPLICATE_TITLE_GROUPS")
    for title, group in sorted(by_title.items()):
        if len(group) > 1:
            print("---")
            print(title)
            for item in group:
                cols = " ; ".join(item["collections"]) if item["collections"] else "[no collection]"
                print(f"{item['key']}\t{item['type']}\t{item['doi']}\t{cols}")

    print("DUPLICATE_PDF_HASH_GROUPS")
    by_hash = defaultdict(list)
    for item in items:
        attachments = cur.execute(
            """
            SELECT a.key, ia.contentType, ia.path
            FROM items a
            JOIN itemAttachments ia ON ia.itemID=a.itemID
            WHERE ia.parentItemID=?
            """,
            (item["itemID"],),
        ).fetchall()
        for att_key, ctype, rel_path in attachments:
            if ctype != "application/pdf" or not rel_path or not rel_path.startswith("storage:"):
                continue
            filename = rel_path.split(":", 1)[1]
            full = storage_root / att_key / filename
            if not full.exists():
                continue
            with open(full, "rb") as fh:
                md5 = hashlib.md5(fh.read()).hexdigest()
            by_hash[md5].append((item, filename, str(full)))

    for md5, owners in sorted(by_hash.items()):
        keys = {item["key"] for item, _, _ in owners}
        if len(keys) > 1:
            print("---")
            print(md5)
            for item, filename, path in owners:
                cols = " ; ".join(item["collections"]) if item["collections"] else "[no collection]"
                print(f"{item['key']}\t{item['title']}\t{filename}\t{cols}\t{path}")


def cmd_integrity(cur):
    orphan_collection_items = cur.execute(
        """
        SELECT ci.collectionID, ci.itemID, i.key, IFNULL(v.value,'[no title]')
        FROM collectionItems ci
        LEFT JOIN collections c ON c.collectionID=ci.collectionID
        JOIN items i ON i.itemID=ci.itemID
        LEFT JOIN itemData d ON d.itemID=i.itemID
          AND d.fieldID=(SELECT fieldID FROM fields WHERE fieldName='title')
        LEFT JOIN itemDataValues v ON v.valueID=d.valueID
        WHERE c.collectionID IS NULL
        ORDER BY ci.collectionID, ci.itemID
        """
    ).fetchall()
    print("ORPHAN_COLLECTIONITEMS", len(orphan_collection_items))
    for row in orphan_collection_items[:100]:
        print("\t".join(str(x) for x in row))

    standalone_attachments = cur.execute(
        """
        SELECT COUNT(*)
        FROM items i
        JOIN itemAttachments ia ON ia.itemID=i.itemID
        LEFT JOIN deletedItems di ON di.itemID=i.itemID
        WHERE di.itemID IS NULL
        AND ia.parentItemID IS NULL
        AND NOT EXISTS (SELECT 1 FROM collectionItems ci WHERE ci.itemID=i.itemID)
        """
    ).fetchone()[0]
    print("STANDALONE_ATTACHMENT_UNFILED", standalone_attachments)


def main():
    parser = argparse.ArgumentParser(description="Audit a local Zotero library safely.")
    parser.add_argument("command", choices=["summary", "unfiled", "duplicates", "integrity"])
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to zotero.sqlite")
    parser.add_argument("--storage-root", default="$HOME/Zotero/storage", help="Zotero storage root")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn, temp_dir = connect_readable(db_path)
    cur = conn.cursor()
    try:
        if args.command == "summary":
            cmd_summary(cur)
        elif args.command == "unfiled":
            cmd_unfiled(cur)
        elif args.command == "duplicates":
            cmd_duplicates(cur, Path(args.storage_root))
        elif args.command == "integrity":
            cmd_integrity(cur)
    finally:
        conn.close()
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
