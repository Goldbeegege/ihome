# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/11/14 9:02


import random
from PIL import Image,ImageDraw,ImageFont,ImageFilter

class Create_Validation_Code:
    """
    self.chars:生成验证码的数字及字母；
    ImageFont.truetype:验证码的字体及字体大小；
    Image.new:生成新的画布，模式是“RGB”彩色，尺寸大小为(100,32); (画布背景为白色(RGB:255,255,255))
    ImageDraw.Draw(self.img):为新的画布生成新的画笔
    self.img.size：画布的尺寸
    """
    def __init__(self):
        self.chars = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.font = ImageFont.truetype("Monaco.ttf",24)
        self.img = Image.new("RGB",(100,32),(255,255,255))
        self.draw = ImageDraw.Draw(self.img)
        self.width,self.height = self.img.size

    def create_random_lines(self):
        """
        生成随机的干扰线，共十条，每条颜色可能不同；
        fill:以什么颜色填充
        """
        for line in range(10):
            line_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            self.draw.line(
                [
                    (random.randint(0,self.width),random.randint(0,self.height)),
                    (random.randint(0,self.width),random.randint(0,self.height))
                ],
                fill=line_color
            )
    def create_random_points(self):
        """
        生成随机干扰点200个；每个点颜色可能不同
        """
        for point in range(200):
            point_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            self.draw.point(
                (random.randint(0,self.width),random.randint(0,self.height)),
                fill=point_color
            )
    def generate_code(self):
        """
        生成验证码
        params：验证码扭曲倾斜的参数；
        text:随机从数字与字母中选取4个
        """
        self.create_random_lines()
        self.create_random_points()
        params  = [
            1-float(random.randint(1,2))/100,
            0,
            0,
            0,
            1-float(random.randint(1,10))/100,
            float(random.randint(1,2))/500,
            0.001,
            float(random.randint(1,2))/500
        ]
        text = " ".join(random.sample(self.chars,4))
        font_width,font_height = self.font.getsize(text)
        self.draw.text(((self.width - font_width)/3,self.height/4),text,fill=(50,50,50),font=self.font)
        self.img.transform((self.width,self.height),Image.PERSPECTIVE,params)
        self.img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        return text.replace(" ",""),self.img

if __name__ == '__main__':
    image = Create_Validation_Code()
    text,img = image.generate_code()
    print(text)
    img.show()