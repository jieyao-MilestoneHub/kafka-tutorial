import os
import json
import argparse

def get_directory_structure(root_dir, exclude_files, base_dir=None):
    """
    遞迴獲取目錄結構，包含資料夾與檔案，
    排除隱藏資料夾、隱藏檔案以及名稱為 venv 的資料夾。
    排除檔案會根據相對於 base_dir 的路徑來比對。
    """
    if base_dir is None:
        base_dir = root_dir

    # 當前目錄節點（若是最上層，則名稱顯示完整路徑）
    node = {
        "name": os.path.basename(root_dir) if os.path.abspath(root_dir) != os.path.abspath(base_dir) else root_dir,
        "type": "directory",
        "children": []
    }

    try:
        items = sorted(os.listdir(root_dir))
    except Exception as e:
        # 如果讀取目錄發生錯誤，則直接回傳錯誤訊息
        return {"name": os.path.basename(root_dir), "type": "directory", "error": str(e)}

    for item in items:
        # 排除隱藏檔案/資料夾與 venv 資料夾
        if item.startswith('.') or item == 'venv':
            continue

        full_path = os.path.join(root_dir, item)
        # 計算從掃描根目錄(base_dir)開始的相對路徑
        relative_path = os.path.relpath(full_path, base_dir)

        if os.path.isdir(full_path):
            child = get_directory_structure(full_path, exclude_files, base_dir)
            node["children"].append(child)
        else:
            # 若此檔案在排除清單中，則跳過
            if relative_path in exclude_files:
                continue
            node["children"].append({
                "name": item,
                "type": "file"
            })
    return node

def get_files_content(root_dir, extensions, exclude_files):
    """
    遍歷目錄樹讀取檔案內容，
    僅針對符合 extensions 指定副檔名的檔案，
    並排除隱藏檔案、隱藏目錄與 venv 目錄，
    以及在 exclude_files 清單中的檔案。
    """
    files_content = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 排除隱藏目錄與 venv 目錄
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != 'venv']
        for filename in filenames:
            # 排除隱藏檔案
            if filename.startswith('.'):
                continue
            file_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
            if file_path in exclude_files:
                continue
            if any(filename.endswith(ext) for ext in extensions):
                try:
                    with open(os.path.join(root_dir, file_path), "r", encoding="utf-8") as f:
                        content = f.read()
                    files_content[file_path] = content
                except Exception as e:
                    files_content[file_path] = f"Error reading file: {e}"
    return files_content

def main():
    parser = argparse.ArgumentParser(description="讀取目錄結構與特定檔案內容，輸出 JSON")
    parser.add_argument("directory", type=str, help="要掃描的目錄")
    parser.add_argument("-e", "--extensions", nargs="+", default=[".py", ".yml"], help="指定要讀取的檔案副檔名")
    parser.add_argument("-o", "--output", type=str, default="output.json", help="輸出的 JSON 檔名")
    parser.add_argument("-x", "--exclude", nargs="*", default=[], help="排除的檔案 (相對路徑)")

    args = parser.parse_args()

    # 建立完整的目錄結構（包含資料夾與檔案）
    directory_structure = get_directory_structure(args.directory, args.exclude)
    # 讀取符合副檔名檔案的內容
    files_content = get_files_content(args.directory, args.extensions, args.exclude)

    result = {
        "directory_structure": directory_structure,
        "files_content": files_content
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"JSON 結果已儲存至 {args.output}")

if __name__ == "__main__":
    main()