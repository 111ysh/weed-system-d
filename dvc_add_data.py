import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class DVCDataAdder:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.resolve()
        self.dvc_initialized = False
        self.git_initialized = False

    def check_dvc_initialized(self) -> bool:
        if (self.project_root / ".dvc").exists():
            self.dvc_initialized = True
            print(f"✓ DVC 已初始化")
            return True
        else:
            print(f"✗ DVC 未初始化")
            return False

    def check_git_initialized(self) -> bool:
        if (self.project_root / ".git").exists():
            self.git_initialized = True
            print(f"✓ Git 已初始化")
            return True
        else:
            print(f"✗ Git 未初始化")
            return False

    def find_data_directories(self) -> List[Path]:
        data_dirs = []

        datasets_dir = self.project_root / "datasets"
        if datasets_dir.exists() and datasets_dir.is_dir():
            raw_dir = datasets_dir / "raw"
            if raw_dir.exists() and raw_dir.is_dir():
                data_dirs.append(raw_dir)

            weights_dir = self.project_root / "weights"
            if weights_dir.exists() and weights_dir.is_dir():
                data_dirs.append(weights_dir)

            demo_samples_dir = self.project_root / "demo_samples"
            if demo_samples_dir.exists() and demo_samples_dir.is_dir():
                data_dirs.append(demo_samples_dir)

        return data_dirs

    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def dvc_add(self, path: Path) -> bool:
        print(f"\n正在添加到 DVC: {path.relative_to(self.project_root)}")
        success, output = self.run_command(["dvc", "add", str(path)])
        if success:
            print(f"  ✓ 成功生成 .dvc 文件")
            return True
        else:
            print(f"  ✗ 失败: {output}")
            return False

    def git_add_dvc_files(self, dvc_files: List[Path]) -> bool:
        print(f"\n正在将 .dvc 文件添加到 Git...")
        for dvc_file in dvc_files:
            if dvc_file.exists():
                success, output = self.run_command(["git", "add", str(dvc_file)])
                if success:
                    print(f"  ✓ {dvc_file.relative_to(self.project_root)}")
                else:
                    print(f"  ✗ {dvc_file.relative_to(self.project_root)}: {output}")
                    return False
        return True

    def update_gitignore(self) -> bool:
        gitignore_path = self.project_root / ".gitignore"
        gitignore_entries = [
            "/datasets/raw",
            "/weights",
            "/demo_samples",
            "*.dvc",
            ".dvc/cache"
        ]

        try:
            if gitignore_path.exists():
                existing_content = gitignore_path.read_text(encoding='utf-8')
            else:
                existing_content = ""

            updated = False
            for entry in gitignore_entries:
                if entry not in existing_content:
                    if existing_content and not existing_content.endswith('\n'):
                        existing_content += '\n'
                    existing_content += entry + '\n'
                    updated = True

            if updated:
                gitignore_path.write_text(existing_content, encoding='utf-8')
                print(f"✓ 已更新 .gitignore")
            else:
                print(f"✓ .gitignore 已包含必要条目")
            return True
        except Exception as e:
            print(f"✗ 更新 .gitignore 失败: {e}")
            return False

    def run(self, add_to_git: bool = False) -> bool:
        print("=" * 60)
        print("DVC 数据提交脚本")
        print("=" * 60)

        if not self.check_dvc_initialized():
            print("\n请先运行 'dvc init' 初始化 DVC")
            return False

        if add_to_git and not self.check_git_initialized():
            print("\n请先运行 'git init' 初始化 Git")
            return False

        data_dirs = self.find_data_directories()
        if not data_dirs:
            print("\n未找到数据目录")
            return False

        print(f"\n找到 {len(data_dirs)} 个数据目录:")
        for d in data_dirs:
            print(f"  - {d.relative_to(self.project_root)}")

        print("\n开始添加数据到 DVC...")
        print("-" * 60)

        dvc_files = []
        success_count = 0

        for data_dir in data_dirs:
            if self.dvc_add(data_dir):
                dvc_file = self.project_root / f"{data_dir.relative_to(self.project_root)}.dvc"
                dvc_files.append(dvc_file)
                success_count += 1

        print("-" * 60)
        print(f"\n完成: {success_count}/{len(data_dirs)} 个目录已添加到 DVC")

        if dvc_files:
            print(f"\n生成的 .dvc 文件:")
            for f in dvc_files:
                if f.exists():
                    print(f"  - {f.relative_to(self.project_root)}")

        if add_to_git and dvc_files:
            self.update_gitignore()
            if self.git_add_dvc_files(dvc_files):
                print(f"\n✓ .dvc 文件已添加到 Git")
                print(f"  提示: 运行 'git commit -m \"Add DVC data files\"' 提交更改")

        print("\n" + "=" * 60)
        print("DVC 数据提交完成")
        print("=" * 60)

        return success_count == len(data_dirs)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DVC 数据提交脚本")
    parser.add_argument(
        "--git",
        action="store_true",
        help="将 .dvc 文件添加到 Git"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=None,
        help="项目根目录路径 (默认为脚本所在目录)"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else None
    adder = DVCDataAdder(project_root)

    success = adder.run(add_to_git=args.git)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
