# -*- coding: utf-8 -*-
"""CS760-HW6_Q2_updated.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18bmhKF_ow5xlOyixCSwwV6ufOHgk7QqC
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torch.optim as optim
import torchvision.datasets as datasets
import imageio
import numpy as np
import matplotlib
from torchvision.utils import make_grid, save_image
from torch.utils.data import DataLoader
from matplotlib import pyplot as plt
from tqdm import tqdm

"""# Define learning parameters"""

# learning parameters
batch_size = 512
epochs = 100
sample_size = 64 # fixed sample size for generator
nz = 128 # latent vector size
k = 1 # number of steps to apply to the discriminator
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

"""# Prepare training dataset"""

transform = transforms.Compose([
                                transforms.ToTensor(),
                                transforms.Normalize((0.5,),(0.5,)),
])
to_pil_image = transforms.ToPILImage()

# Make input, output folders
!mkdir -p input
!mkdir -p outputs

# Load train data
train_data = datasets.MNIST(
    root='input/data',
    train=True,
    download=True,
    transform=transform
)
train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)

"""# Generator"""

class Generator(nn.Module):
    def __init__(self, nz):
        super(Generator, self).__init__()
        self.nz = nz
        self.main = nn.Sequential(
            nn.Linear(self.nz, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, 784),
            nn.Tanh(),
        )
    def forward(self, x):
        return self.main(x).view(-1, 1, 28, 28)

"""# Discriminator"""

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.n_input = 784
        self.main = nn.Sequential(
            nn.Linear(self.n_input, 1024),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )
    def forward(self, x):
        x = x.view(-1, 784)
        return self.main(x)

generator = Generator(nz).to(device)
discriminator = Discriminator().to(device)
print('##### GENERATOR #####')
print(generator)
print('######################')
print('\n##### DISCRIMINATOR #####')
print(discriminator)
print('######################')

"""# Tools for training"""

# optimizers
optim_g = optim.Adam(generator.parameters(), lr=0.0002)
optim_d = optim.Adam(discriminator.parameters(), lr=0.0002)

# loss function
criterion = nn.BCELoss() # Binary Cross Entropy loss

losses_g = [] # to store generator loss after each epoch
losses_d = [] # to store discriminator loss after each epoch
images = [] # to store images generatd by the generator

# to create real labels (1s)
def label_real(size):
    data = torch.ones(size, 1)
    return data.to(device)
# to create fake labels (0s)
def label_fake(size):
    data = torch.zeros(size, 1)
    return data.to(device)

# function to create the noise vector
def create_noise(sample_size, nz):
    return torch.randn(sample_size, nz).to(device)

# to save the images generated by the generator
def save_generator_image(image, path):
    save_image(image, path)

# create the noise vector - fixed to track how GAN is trained.
noise = create_noise(sample_size, nz)

"""# Q. Write training loop"""

torch.manual_seed(7777)

def generator_loss(output, true_label):
    ############ YOUR CODE HERE ##########
    return -criterion(output,true_label)


    ######################################

def discriminator_loss(output, true_label):
    ############ YOUR CODE HERE ##########
    loss = criterion(output, true_label)
    return loss

    ######################################


for epoch in range(epochs):
    loss_g = 0.0
    loss_d = 0.0
    for bi, data in tqdm(enumerate(train_loader), total=int(len(train_data)/train_loader.batch_size)):
      ############ YOUR CODE HERE ##########

      ##Training Discriminator
      real_data, _ = data
      real_data = real_data.cuda()

      batch_size = real_data.shape[0]
      optim_d.zero_grad()
      ##Train on Real data
      predictions_real = discriminator(real_data).view(-1)

      target_real = label_real(predictions_real.shape[0]).squeeze(1)
      disc_loss_real = discriminator_loss(predictions_real, target_real)
      disc_loss_real.backward()

      rand_noise = create_noise(batch_size, nz)
      fake_images = generator(rand_noise)
      predictions_fake = discriminator(fake_images.detach()).view(-1)

      target_fake = label_fake(predictions_fake.shape[0]).squeeze(1)
      disc_loss_fake = discriminator_loss(predictions_fake, target_fake)
      disc_loss_fake.backward()
      optim_d.step()


      loss_d += disc_loss_real + disc_loss_fake

      ##Generator Training
      optim_g.zero_grad()
      rand_noise = create_noise(batch_size, nz)
      fake_images = generator(rand_noise)
      predictions_disc = discriminator(fake_images).view(-1)

      target_fake_generator = label_fake(predictions_disc.shape[0]).squeeze(1)
      loss_generator = generator_loss(predictions_disc, target_fake_generator)

      loss_generator.backward()

      loss_g += loss_generator

      optim_g.step()



        ######################################


    # create the final fake image for the epoch
    generated_img = generator(noise).cpu().detach()

    # make the images as grid
    generated_img = make_grid(generated_img)

    # visualize generated images
    if (epoch + 1) % 5 == 0:
        plt.imshow(generated_img.permute(1, 2, 0))
        plt.title(f'epoch {epoch+1}')
        plt.axis('off')
        plt.show()

    # save the generated torch tensor models to disk
    save_generator_image(generated_img, f"outputs/gen_img{epoch+1}.png")
    images.append(generated_img)
    epoch_loss_g = loss_g / bi # total generator loss for the epoch
    epoch_loss_d = loss_d / bi # total discriminator loss for the epoch
    losses_g.append(epoch_loss_g)
    losses_d.append(epoch_loss_d)

    print(f"Epoch {epoch+1} of {epochs}")
    print(f"Generator loss: {epoch_loss_g:.8f}, Discriminator loss: {epoch_loss_d:.8f}")

print('DONE TRAINING')
torch.save(generator.state_dict(), 'outputs/generator.pth')

# save the generated images as GIF file
imgs = [np.array(to_pil_image(img)) for img in images]
imageio.mimsave('outputs/generator_images.gif', imgs)

# # plot and save the generator and discriminator loss

numpy_list_d = [tensor.cpu().detach().numpy() for tensor in losses_d]
numpy_list_g = [tensor.cpu().detach().numpy() for tensor in losses_g]
plt.figure()
plt.plot(numpy_list_g, label='Generator loss')
plt.plot(numpy_list_d, label='Discriminator Loss')
plt.legend()
plt.savefig('outputs/loss.png')

# # plot and save the generator and discriminator loss
# plt.figure()
# plt.plot(losses_g, label='Generator loss')
# plt.plot(losses_d, label='Discriminator Loss')
# plt.legend()
# plt.savefig('outputs/loss.png')

import shutil

# Define the path to the folder you want to zip
folder_path = '/content/outputs'  # Update this with your folder path

# Define the name for the zip file
zip_filename = '/content/outputs_new_2_1.zip'  # Update this with your desired zip file name

# Zip the folder
shutil.make_archive(zip_filename.split('.zip')[0], 'zip', folder_path)

