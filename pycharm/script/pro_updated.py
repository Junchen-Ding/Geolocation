import os
import requests
import tarfile
import zipfile
import rarfile
import py7zr
import pytorch_lightning as pl
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import io
import re


# 考虑视频及图像的可能形式
class CustomDataset(Dataset):
    def __init__(self, file_paths, transform=None):
        self.file_paths = file_paths
        self.transform = transform

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            with open(file_path, 'rb') as f:
                image = Image.open(io.BytesIO(f.read())).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image
        elif file_path.lower().endswith(('mp4', 'avi', 'mov', 'mkv', 'flv')):
            # 读取视频帧，读取视频的第一帧
            import cv2
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                image = Image.fromarray(frame)
                if self.transform:
                    image = self.transform(image)
                return image
        else:
            raise ValueError(f"Unsupported file format: {file_path}")


# 用于处理数据ImageDataModule
class ImageDataModule(pl.LightningDataModule):
    def __init__(self, data_dir, batch_size=32, num_workers=4):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    def setup(self, stage=None):
        if stage in (None, 'fit', 'validate', 'test'):
            self.train_dataset = CustomDataset(
                file_paths=self.get_file_paths(self.data_dir),
                transform=self.transform
            )

    def get_file_paths(self, dir):
        file_paths = []
        for root, _, files in os.walk(dir):
            for file in files:
                if file.lower().endswith(
                        ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.mp4', '.avi', '.mov', '.mkv', '.flv')):
                    file_paths.append(os.path.join(root, file))
        return file_paths

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=True)


def main():
    markdown_file_path = input("Please enter the full path to the markdown file: ").strip()
    resource_dir = './resources'

    os.makedirs(resource_dir, exist_ok=True)

    def extract_dataset_links(markdown_content):
        dataset_links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', markdown_content)
        return dataset_links

    def download_and_extract(url, extract_to):
        local_filename = url.split('/')[-1]
        local_path = os.path.join(extract_to, local_filename)

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        if local_path.endswith('.tar.gz') or local_path.endswith('.tgz'):
            with tarfile.open(local_path, 'r:gz') as tar:
                tar.extractall(path=extract_to)
        elif local_path.endswith('.zip'):
            with zipfile.ZipFile(local_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif local_path.endswith('.rar'):
            with rarfile.RarFile(local_path, 'r') as rar_ref:
                rar_ref.extractall(extract_to)
        elif local_path.endswith('.7z'):
            with py7zr.SevenZipFile(local_path, 'r') as z:
                z.extractall(extract_to)
        else:
            # If the file is not an archive, just download it directly to the folder.
            print(f"{local_filename} is not an archive, saved directly.")

    # main 函数中的主要逻辑，下载并提取数据集
    if not os.path.exists(markdown_file_path):
        print(f"File not found: {markdown_file_path}")
        return

    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    links_with_names = extract_dataset_links(markdown_content)

    while True:
        print("The link to the extracted dataset is as follows:")
        for idx, (name, link) in enumerate(links_with_names, start=1):
            print(f"{idx}. {name}")

        while True:
            try:
                chosen_index = int(input("Please enter the identifier of the dataset you want to download: ").strip())
                if 1 <= chosen_index <= len(links_with_names):
                    break
                else:
                    print(f"Invalid marker, please enter a value between 1 and {len(links_with_names)}")
            except ValueError:
                print("Please enter a valid number")

        chosen_name, chosen_link = links_with_names[chosen_index - 1]
        print(f"Selected datasets： {chosen_name}")

        print(f"Downloading and unpacking: {chosen_name}")
        download_and_extract(chosen_link, resource_dir)
        print(f"The dataset {chosen_name} has been downloaded and extracted.")

        while True:
            continue_download = input("Do you continue to download other datasets? (Y/N): ").strip().upper()
            if continue_download in ['Y', 'N']:
                break
            else:
                print("Invalid input, please enter Y or N")

        if continue_download == 'N':
            break

    # 设置并使用 ImageDataModule
    data_module = ImageDataModule(data_dir=resource_dir)
    data_module.setup('fit')

    # 打印训练数据集的样本数
    if data_module.train_dataset:
        print(f"Number of samples in the training dataset: {len(data_module.train_dataset)}")
    else:
        print("Training dataset not found, make sure data directory structure is correct")


if __name__ == "__main__":
    main()
