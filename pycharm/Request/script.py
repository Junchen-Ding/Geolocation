import os
import requests
from bs4 import BeautifulSoup
import zipfile
import tarfile
from torch.utils.data import DataLoader, Dataset
import pytorch_lightning as pl
from torchvision import transforms, datasets


def download_and_extract(url, extract_to='resource', download_only=False):
    # Create the resource directory if it doesn't exist
    os.makedirs(extract_to, exist_ok=True)
    session = requests.Session()
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    for link in soup.find_all('a'):
        file_name = link.get('href')
        if not file_name:
            continue

        file_url = url + file_name
        file_path = os.path.join(extract_to, file_name)

        # Download the file
        print(f'Downloading {file_name}...')
        file_response = session.get(file_url)
        with open(file_path, 'wb') as file:
            file.write(file_response.content)

        if not download_only and (
                file_name.endswith('.zip') or file_name.endswith('.tgz') or file_name.endswith('.tar.gz')):
            # Extract the file
            print(f'Extracting {file_name}...')
            if file_name.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif file_name.endswith('.tgz') or file_name.endswith('.tar.gz'):
                with tarfile.open(file_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_to)
            os.remove(file_path)


# URL of the dataset
dataset_url = 'https://www.cis.jhu.edu/~shraman/TransLocator/Datasets/'
annotations_url = 'https://www.cis.jhu.edu/~shraman/TransLocator/Annotations/'

# Download and extract datasets
download_and_extract(dataset_url)

# Download annotations only
download_and_extract(annotations_url, download_only=True)


# Define a custom dataset class
class CustomDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.dataset = datasets.ImageFolder(data_dir, transform=transform)

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        return self.dataset[idx]


# Define a PyTorch Lightning DataModule
class CustomDataModule(pl.LightningDataModule):
    def __init__(self, data_dir='resource', batch_size=32):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.transform = transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
        ])

    def prepare_data(self):
        # Data download and extraction already handled above
        pass

    def setup(self, stage=None):
        self.train_dataset = CustomDataset(os.path.join(self.data_dir, 'train'), transform=self.transform)
        self.val_dataset = CustomDataset(os.path.join(self.data_dir, 'val'), transform=self.transform)
        self.test_dataset = CustomDataset(os.path.join(self.data_dir, 'test'), transform=self.transform)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size)


# Example usage
data_module = CustomDataModule()
trainer = pl.Trainer(max_epochs=5)
# Assume you have a model defined as `model`
# trainer.fit(model, data_module)
