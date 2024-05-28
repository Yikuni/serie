import torch
from torch import nn
from torchvision.io import read_image
class LeNet(nn.Module):
    def __init__(self, **kwargs):
        super(LeNet, self).__init__(**kwargs)
        self.c1 = nn.Conv2d(3, 6, kernel_size=5)  # (6, 60, 60)
        self.a1 = nn.Sigmoid()
        self.p1 = nn.MaxPool2d(kernel_size=2, stride=2)  # (6, 30, 30)
        self.c2 = nn.Conv2d(6, 16, kernel_size=5)  # (16, 26, 26)
        self.a2 = nn.Sigmoid()
        self.p2 = nn.MaxPool2d(kernel_size=2, stride=2)  # (16, 13, 13)
        self.flatten = nn.Flatten()
        self.f1 = nn.Linear(16 * 13 * 13, 240)
        self.a3 = nn.Sigmoid()
        self.f2 = nn.Linear(240, 84)
        self.a4 = nn.Sigmoid()
        self.f3 = nn.Linear(84, 3)

    def forward(self, X):
        X = self.c1(X)
        X = self.a1(X)
        X = self.p1(X)
        X = self.c2(X)
        X = self.a2(X)
        X = self.p2(X)
        X = self.flatten(X)
        X = self.f1(X)
        X = self.a3(X)
        X = self.f2(X)
        X = self.a4(X)
        X = self.f3(X)
        return X
def predict(net, image_path):
    net.eval()
    img = read_image(image_path) / 255
    img = torch.unsqueeze(img, dim=0)
    return torch.argmax(net(img),  dim=1)
