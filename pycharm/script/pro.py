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
class CustomDataset(Dataset) :
    def __init__(self, file_paths, transform=None) :
        self.file_paths = file_paths
        self.transform = transform

    def __len__(self) :
        return len(self.file_paths)

    def __getitem__(self, idx) :
        file_path = self.file_paths[idx]
        if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')) :
            with open(file_path, 'rb') as f :
                image = Image.open(io.BytesIO(f.read())).convert('RGB')
            if self.transform :
                image = self.transform(image)
            return image
        elif file_path.lower().endswith(('mp4', 'avi', 'mov', 'mkv', 'flv')) :
            # 读取视频帧，读取视频的第一帧
            import cv2
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            cap.release()
            if ret :
                image = Image.fromarray(frame)
                if self.transform :
                    image = self.transform(image)
                return image
        else :
            raise ValueError(f"Unsupported file format: {file_path}")


# 用于处理数据ImageDataModule
class ImageDataModule(pl.LightningDataModule) :
    def __init__(self, data_dir, batch_size=32, num_workers=4) :
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    def setup(self, stage=None) :
        if stage in (None, 'fit', 'validate', 'test') :
            self.train_dataset = CustomDataset(
                file_paths=self.get_file_paths(), transform=self.transform)

    def get_file_paths(self) :
        file_paths = set()
        for root, _, files in os.walk(self.data_dir) :
            for file in files :
                file_name = os.path.splitext(file)[0]
                file_paths.add(os.path.join(root, file_name))
        return list(file_paths)

    def train_dataloader(self) :
        return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=True)


def parse_markdown(file_path) :
    try :
        with open(file_path, 'r', encoding='utf-8') as file :
            markdown_content = file.read()
        return markdown_content
    except FileNotFoundError :
        print(f"File not found: {file_path}")
        return None


def extract_dataset_links(markdown_content) :
    # 使用正则表达式提取所有的链接和名称
    links_with_names = re.findall(r'\[(.*?)\]\((https?://.*?)\)', markdown_content)
    return links_with_names


def download_and_extract(url, download_path) :
    file_name = os.path.join(download_path, url.split('/')[-1])
    response = requests.get(url, stream=True)
    with open(file_name, 'wb') as file :
        for chunk in response.iter_content(chunk_size=1024) :
            if chunk :
                file.write(chunk)

    # 判断文件类型并解压
    if file_name.endswith(('tar.gz', 'tgz')) :
        with tarfile.open(file_name, 'r:gz') as tar :
            tar.extractall(path=download_path)
    elif file_name.endswith('tar') :
        with tarfile.open(file_name, 'r') as tar :
            tar.extractall(path=download_path)
    elif file_name.endswith('zip') :
        with zipfile.ZipFile(file_name, 'r') as zip_ref :
            zip_ref.extractall(download_path)
    elif file_name.endswith('rar') :
        with rarfile.RarFile(file_name, 'r') as rar_ref :
            rar_ref.extractall(download_path)
    elif file_name.endswith('7z') :
        with py7zr.SevenZipFile(file_name, 'r') as seven_z_ref :
            seven_z_ref.extractall(download_path)
    else :
        print(f"Unsupported file format for extraction: {file_name}")
    os.remove(file_name)


def main() :
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resource_dir = os.path.join(script_dir, 'resource')
    if not os.path.exists(resource_dir) :
        os.makedirs(resource_dir)

    while True :
        file_path = input("Please enter the path to the Markdown file: ").strip()
        if os.path.isfile(file_path) :
            break
        else :
            print(f"Invalid file path: {file_path}，please re-enter。")

    markdown_content = parse_markdown(file_path)
    if markdown_content :
        print("The contents of the file have been read")
        links_with_names = extract_dataset_links(markdown_content)

        while True :
            print("The link to the extracted dataset is as follows:")
            for idx, (name, link) in enumerate(links_with_names, start=1) :
                print(f"{idx}. {name}")

            while True :
                try :
                    chosen_index = int(input("Please enter the identifier of the dataset you want to download: ").strip())
                    if 1 <= chosen_index <= len(links_with_names) :
                        break
                    else :
                        print(f"Invalid marker, please enter a value between 1 and {len(links_with_names)}")
                except ValueError :
                    print("Please enter a valid number")

            chosen_name, chosen_link = links_with_names[chosen_index - 1]
            print(f"Selected datasets： {chosen_name}")

            print(f"Downloading and unpacking: {chosen_name}")
            download_and_extract(chosen_link, resource_dir)
            print(f"The dataset {chosen_name} has been downloaded and extracted.")

            while True :
                continue_download = input("Do you continue to download other datasets? (Y/N): ").strip().upper()
                if continue_download in ['Y', 'N'] :
                    break
                else :
                    print("Invalid input, please enter Y or N")

            if continue_download == 'N' :
                break

    # 设置并使用 ImageDataModule
    data_module = ImageDataModule(data_dir=resource_dir)
    data_module.setup('fit')

    # 打印训练数据集的样本数
    if data_module.train_dataset :
        print(f"Number of samples in the training dataset: {len(data_module.train_dataset)}")
    else :
        print("Training dataset not found, make sure data directory structure is correct")

if __name__ == "__main__" :
    main()
