# cprdspy创意编程（一）
## 简介
**cprdspy**是一个基于Python的可视化创意编程工具，可以生成各式各样好看的图片。<br/>
**cprdspy**的全称是**Circle Point Round Dot Surface Pyramid**，中文翻译为圈点圆面金字塔。从名字可以看出它涉及的元素有圆圈，点，面和线段，最基础的则是圈和点。因为圈和点互为阴阳，圈缩一粒为点，点绕一转为圈，圈点足以创造出二元对立世界的一切：因为由基本粒子物理学我们知道构成世界的物质非物质不过是一些点粒子，而超弦理论或M理论又说基本粒子实际上是或开或闭的弦，可以理解为圆弧的拼接或圆弧的变换。因此，掌握圈和点我们便能创造出很多妙不可言的美好。
>圈点不仅涉及数学和整个科学，它还与艺术设计密不可分，不信你们可以去查，诸如苹果和很多公司的logo都是由最基本的圆弧和点线段构成的，可以这么说，圈点是艺术的天下，而本文将逐步介绍如何用cprdspy创造出这些令人惊奇的艺术品。

**先上图看看**：
| 睡莲                      | 一种不知名花              |
| ------------------------- | ------------------------- |
| ![alt text](image-29.png) | ![alt text](image-28.png) |
| 基础环面                  | 曼陀罗花和睡莲的结合体    |
| ![alt text](image-30.png) | ![alt text](image-31.png) |
| 11瓣的水莲花              | 八角正方形的star          |
| ![alt text](image-32.png) | ![alt text](image-33.png) |
| 公园里的荷花形状          | 椭圆弧的花                |
| ![alt text](image-34.png) | ![alt text](image-35.png) |


## 环境搭建
“工欲善其事，必先利其器。”，现在，我们就开始为我们的艺术品创造搭建环境。过去的艺术品诸如绘画，雕塑，书法，都是由手工制作，而现在，我们将使用思维的工具**cprdspy**来制作。什么是思维的工具呢？很多同学想必已经猜到了，没错，那就是程序。首先，我们得有一台足够强大的可编程的电脑，在电脑中装入如Python那样的程序编译器，再安装我们的创意编程工具cprdspy，就可以进行艺术创作了！当然，有的同学会走得更远，它们还会安装诸如VSCode那样的代码编辑器方便我们的开发创作，不过这些都不是问题，后面的步骤中我都会一一教给大家，所以编程小白放心吧！
1. 下载并安装Python
   - 下载Python,打开官网 https://www.python.org/ 如下图，点击Downloads![alt text](image.png)
   点击按钮下载当前最新版：
   ![alt text](image-1.png)
   - 得到安装包并安装Python：
    ![alt text](image-2.png)
    单击打开文件或：
    ![alt text](image-3.png)
    在下载文件夹中双击文件运行安装程序：
    ![alt text](image-4.png)
    记得勾选下面两个复选框然后点击Customize installation
    ![alt text](image-5.png)
    默认点击Next(下一步)
    ![alt text](image-6.png)
    勾选红框中的所有选项然后点击Install(安装)
    ![alt text](image-7.png)
    安装中......
    ![alt text](image-8.png)
    安装完成！
    
2. 安装cprdspy(一般安装方法，可跳过直接看3.)
   - 打开cmd(Windows+R,输入cmd,确定)或Powershell终端
   ![alt text](image-9.png)
   - 输入：
       ```python
       pip install cprdspy
       ```
       ![alt text](image-10.png)
   - 等待安装完成
   ![alt text](image-11.png)
   - 安装完成 
3. 开始编程画图：
   - 首先创建一个文件夹取你喜欢的名字(一定是英文名或拼音)，
    这里我取名为cpr(因为我这里是中文名运行不了uv相关命令后改的文件名，所以图有一点不一样，大家请先改文件名)<br/>
       ![alt text](image-12.png)
       ![alt text](image-26.png)
       <br>
       打开并进入文件夹后右键选择“在终端中打开”
       ![alt text](image-13.png)
        在终端中输入：
        ```bash
        pip install uv
        ```
        ![alt text](image-14.png)
        接着输入：
        ```bash
        uv init
        ```
        ![alt text](image-15.png)
        然后输入：
        ```bash
        uv add cprdspy
        ```
        ![alt text](image-16.png)
        ![alt text](image-17.png)
        接着输入：
        ```bash
        .venv\Scripts\activate
        ```
        ![alt text](image-18.png)
        返回文件夹，新建文本文件取名test
        ![alt text](image-19.png)
        粘贴代码：
        ```python
        from cprdspy.CPR_matplotlib import *
        from matplotlib import pyplot as plt
        flowers_mpl()
        plt.show()
        ```
        ![alt text](image-20.png)
        保存并退出
        ![alt text](image-21.png)
        显示文件扩展名
        ![alt text](image-22.png)
        将代码文件扩展名改为py
        ![alt text](image-23.png)
        再按右键“在终端中打开”，输入：
        ```bash
        .venv\Scripts\activate
        ```
        ![alt text](image-25.png)
        当PS前面出现(cpr)或其他你的文件夹名时就可以运行Python代码了
        ```bash
        python -u .\test.py
        ```
        ![alt text](image-24.png)
        按下回车键就可以看到画图结果了！
        ![alt text](image-27.png)
        这就是我们的比例为$\sqrt{2}$的12瓣睡莲
        ![alt text](image-36.png)

## 画图的函数
图虽然画出来了，程序也运行了，但究竟是什么原因才能画出这个好看的图形呢？我们只写了4行代码，前两行用于导入相关功能库，最后一行用于显示图形，那么聪明的你肯定猜到了关键代码在第4行，没错，就是这个函数：
```python
flowers_mpl()
```
我们可以看看它的API,展开.venv文件夹下的Lib文件夹中的site-packages文件夹内的cprdspy，里面有一个CPR_matplotlib文件夹，点击里面的Flowers中的flower.py文件
![alt text](image-37.png)
![alt text](image-38.png)
![alt text](image-39.png)
搜索flowers()函数，可以看到它的函数头定义如下：
```python
 flowers(
    R=1,
    r=1,
    n=4,
    ratio=np.sqrt(2),
    M=3,
    N=12,
    color="b",
    alpha=1,
    theta=0,
    center=(0, 0),
    points=1000,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="b",
    markeredgewidth=1,
    ax=None,
    plot_center=False,
    center_color="r",
    center_size=5,
    use_degree=False,
    plot=True,
    direction="ccw",
    return_flower=False,
    **kwargs,
)
```
我们只需要关注前几项：
```python
flowers(
    R=1,
    r=1,
    n=4,
    ratio=np.sqrt(2),
    M=3,
    N=12,
    color="b",
    alpha=1,
    theta=0,
    center=(0, 0),
    points=1000
)
```
- R：外圆半径
- r：内圆半径
- n：圆周上n个点
- ratio：外花内花的半径比
- M：花的层数
- N：一层内花的瓣数
- color：颜色
- alpha：透明度
- theta：旋转角度
- center：中心点坐标
- points：花弧精度

这样想必大家就会DIY花朵了
比如我们刚刚画的$\sqrt{2}$睡莲可以这样写
```python
import numpy as np #之前的两个库请自行导入
flowers_mpl(1,1,4,np.sqrt(2),3,12)
```
至于为什么是flowers_mpl而不是flowers，因为flowers是flowers_mpl的别名，在Python库导出时为了区别plotly版本的我才以mpl简写代表它是matplotlib版本，所以我们直接使用flowers_mpl即可。

## 结束语
好了，想必大家都画出了自己的第一朵睡莲，那么本章的目的已完成，下一章我们将继续学习如何画出更多花朵，以及用VSCode作为我们的专业开发环境，期待大家迸发出创意的灵感！