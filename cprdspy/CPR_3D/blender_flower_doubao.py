"""
Blender 花瓣网格生成器（NumPy加速）

优化特性：
- 向量化计算，弧线生成速度更快
- 材质缓存机制，避免重复创建
- 内存高效数组处理
- 完整的类型注解
- 更完善的错误处理与参数校验
- 资源清理工具
- 减少冗余计算
- 可配置默认参数

用法：在Blender脚本工作区运行，提供create_petal函数创建花瓣网格
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass


# --------------------------
# 配置常量（集中管理默认参数）
# --------------------------
@dataclass(frozen=True)
class PetalDefaults:
    """花瓣生成的统一默认参数"""

    外半径: float = 1.0
    弧半径: float = 1.0
    花瓣性质: int = 4
    旋转角度: float = 0.0
    中心坐标: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    采样点数: int = 2048
    厚度: float = 0.0
    封口: bool = True
    颜色: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    线宽: int = 1
    发光强度: float = 1.0
    使用角度制: bool = True


# --------------------------
# Blender 依赖（延迟加载）
# --------------------------
class BlenderContext:
    """
    延迟加载Blender相关模块
    避免在非Blender环境中出现导入错误
    """

    _bpy = None
    _Matrix = None
    _Vector = None

    @classmethod
    def setup(cls):
        if cls._bpy is None:
            try:
                import bpy
                from mathutils import Matrix, Vector

                cls._bpy = bpy
                cls._Matrix = Matrix
                cls._Vector = Vector
            except ImportError:
                pass

    @classmethod
    def get_bpy(cls):
        cls.setup()
        return cls._bpy

    @classmethod
    def get_matrix(cls):
        cls.setup()
        return cls._Matrix


# --------------------------
# 核心计算函数
# --------------------------
def 校验花瓣参数(外半径: float, 弧半径: float, 花瓣性质: int, 采样点数: int) -> None:
    """校验输入参数，防止数值错误"""
    if 外半径 <= 0:
        raise ValueError(f"外半径必须为正数 (输入值: {外半径})")
    if 弧半径 <= 0:
        raise ValueError(f"弧半径必须为正数 (输入值: {弧半径})")
    if 花瓣性质 < 3:
        raise ValueError(f"花瓣性质至少为3 (输入值: {花瓣性质})")
    if 采样点数 < 2:
        raise ValueError(f"采样点数至少为2 (输入值: {采样点数})")


def 计算花瓣弧线(
    外半径: float = PetalDefaults.外半径,
    弧半径: float = PetalDefaults.弧半径,
    花瓣性质: int = PetalDefaults.花瓣性质,
    旋转角度: float = PetalDefaults.旋转角度,
    中心坐标: Tuple[float, float] = (0.0, 0.0),
    采样点数: int = PetalDefaults.采样点数,
    使用角度制: bool = PetalDefaults.使用角度制,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    使用NumPy向量化计算花瓣的两条对称弧线
    返回：(弧线1点集, 弧线2点集)，格式为(N,2)
    """
    校验花瓣参数(外半径, 弧半径, 花瓣性质, 采样点数)

    # 预计算固定角度，减少三角函数调用
    总角度 = 2.0 * np.pi / 花瓣性质
    半角 = 总角度 / 2.0
    π除以n = np.pi / 花瓣性质
    临时值 = 外半径 * np.sin(π除以n)

    # 安全反余弦计算，防止数值越界
    比值 = np.clip(临时值 / 弧半径, -1.0, 1.0)
    β角 = np.arccos(比值)
    弧线角 = (np.pi / 2) - π除以n + β角

    # 旋转角度转换
    旋转弧度 = np.radians(旋转角度) if 使用角度制 else float(旋转角度)

    # 圆心计算
    圆心角1 = 旋转弧度 + 半角
    圆心角2 = 旋转弧度 - 半角

    cos1, sin1 = np.cos(圆心角1), np.sin(圆心角1)
    cos2, sin2 = np.cos(圆心角2), np.sin(圆心角2)

    圆心1 = np.array([cos1 * 外半径 + 中心坐标[0], sin1 * 外半径 + 中心坐标[1]])
    圆心2 = np.array([cos2 * 外半径 + 中心坐标[0], sin2 * 外半径 + 中心坐标[1]])

    # 角度采样
    点数1 = 采样点数 // 2
    点数2 = 采样点数 - 点数1

    # 基础角度
    基础角1 = np.pi + 半角
    基础角2 = 基础角1 + 弧线角
    基础角3 = (np.pi / 2) - β角
    基础角4 = 基础角3 + 弧线角

    # 生成角度序列
    t1 = np.linspace(基础角1, 基础角2, 点数1, endpoint=True, dtype=np.float64)
    t2 = np.linspace(基础角3, 基础角4, 点数2, endpoint=True, dtype=np.float64)

    # 向量化计算弧线坐标
    弧线1 = 圆心1[:, None] + 弧半径 * np.array([np.cos(t1), np.sin(t1)])
    弧线2 = 圆心2[:, None] + 弧半径 * np.array([np.cos(t2), np.sin(t2)])

    # 转换为标准格式
    点集1 = 弧线1.T if 弧线1.size > 0 else np.empty((0, 2), dtype=np.float64)
    点集2 = 弧线2.T if 弧线2.size > 0 else np.empty((0, 2), dtype=np.float64)

    # 容错处理
    if 点集1.size == 0:
        点集1 = np.flipud(点集2) if 点集2.size > 0 else np.empty((0, 2))
    if 点集2.size == 0:
        点集2 = np.flipud(点集1) if 点集1.size > 0 else np.empty((0, 2))

    if 点集1.size == 0 and 点集2.size == 0:
        raise ValueError("未生成有效弧线点，请检查参数")

    return 点集1, 点集2


# --------------------------
# 材质缓存（避免重复创建）
# --------------------------
_材质缓存: Dict[str, Any] = {}


def 获取或创建发光材质(
    名称: str,
    颜色: Tuple[float, float, float, float] = PetalDefaults.颜色,
    发光强度: float = PetalDefaults.发光强度,
) -> Any:
    """获取缓存材质或创建新材质，仅在Blender环境有效"""
    bpy = BlenderContext.get_bpy()
    if bpy is None:
        return None

    缓存键 = f"{名称}_{颜色}_{发光强度}"
    if 缓存键 in _材质缓存:
        return _材质缓存[缓存键]

    # 创建材质
    材质 = bpy.data.materials.new(name=f"材质_{名称}_发光")
    材质.use_nodes = True
    节点 = 材质.node_tree.nodes
    连线 = 材质.node_tree.links

    # 清空默认节点
    for 节点项 in list(节点):
        节点.remove(节点项)

    # 创建发光着色器
    发光节点 = 节点.new(type="ShaderNodeEmission")
    发光节点.inputs["Color"].default_value = 颜色
    发光节点.inputs["Strength"].default_value = 发光强度

    输出节点 = 节点.new(type="ShaderNodeOutputMaterial")
    连线.new(发光节点.outputs["Emission"], 输出节点.inputs["Surface"])

    # 存入缓存
    _材质缓存[缓存键] = 材质
    return 材质


# --------------------------
# 主函数：创建单个花瓣
# --------------------------
def 创建花瓣(
    名称: str,
    外半径: float = PetalDefaults.外半径,
    弧半径: float = PetalDefaults.弧半径,
    花瓣性质: int = PetalDefaults.花瓣性质,
    旋转角度: float = PetalDefaults.旋转角度,
    中心坐标: Tuple[float, float, float] = PetalDefaults.中心坐标,
    采样点数: int = PetalDefaults.采样点数,
    厚度: float = PetalDefaults.厚度,
    封口: bool = PetalDefaults.封口,
    材质: Optional[Any] = None,
    颜色: Tuple[float, float, float, float] = PetalDefaults.颜色,
    线宽: int = PetalDefaults.线宽,
    发光强度: float = PetalDefaults.发光强度,
    使用角度制: bool = PetalDefaults.使用角度制,
) -> Any:
    """
    创建优化版Blender花瓣对象
    核心优化：向量化计算、材质缓存、内存高效、延迟加载
    """
    # 生成2D弧线点
    点集1, 点集2 = 计算花瓣弧线(
        外半径=外半径,
        弧半径=弧半径,
        花瓣性质=花瓣性质,
        旋转角度=0.0,
        中心坐标=(中心坐标[0], 中心坐标[1]),
        采样点数=采样点数,
        使用角度制=使用角度制,
    )

    # 转换为3D顶点
    顶点1 = (
        np.hstack([点集1, np.full((len(点集1), 1), 中心坐标[2], dtype=np.float64)])
        if len(点集1) > 0
        else np.empty((0, 3))
    )
    顶点2 = (
        np.hstack([点集2, np.full((len(点集2), 1), 中心坐标[2], dtype=np.float64)])
        if len(点集2) > 0
        else np.empty((0, 3))
    )

    # 非Blender环境返回数据
    bpy = BlenderContext.get_bpy()
    if bpy is None:

        def 获取边(顶点数组: np.ndarray) -> np.ndarray:
            if len(顶点数组) < 2:
                return np.empty((0, 2), dtype=int)
            return np.column_stack(
                [np.arange(len(顶点数组) - 1), np.arange(1, len(顶点数组))]
            )

        return {
            "弧线1": {"顶点": 顶点1.astype(np.float32), "边": 获取边(顶点1)},
            "弧线2": {"顶点": 顶点2.astype(np.float32), "边": 获取边(顶点2)},
            "元数据": {
                "厚度": float(厚度),
                "颜色": tuple(颜色),
                "线宽": int(线宽),
                "发光强度": float(发光强度),
            },
        }

    # Blender环境创建曲线
    Matrix = BlenderContext.get_matrix()

    # 新建曲线数据
    曲线数据 = bpy.data.curves.new(name=f"{名称}_曲线", type="CURVE")
    曲线数据.dimensions = "3D"
    曲线数据.bevel_depth = float(max(0.0, 厚度))
    曲线数据.bevel_resolution = max(0, int(线宽))

    # 添加样条线
    def 添加样条(顶点数组: np.ndarray):
        if len(顶点数组) == 0:
            return
        样条 = 曲线数据.splines.new(type="POLY")
        样条.points.add(len(顶点数组) - 1)
        点数据 = np.array([(v[0], v[1], v[2], 1.0) for v in 顶点数组], dtype=np.float32)
        样条.points.foreach_set("co", 点数据.ravel())
        样条.use_cyclic_u = False

    添加样条(顶点1)
    添加样条(顶点2)

    # 创建对象并链接到场景
    对象 = bpy.data.objects.new(名称, 曲线数据)
    bpy.context.collection.objects.link(对象)

    # 应用旋转
    if 旋转角度 != 0:
        旋转弧度 = np.radians(旋转角度) if 使用角度制 else float(旋转角度)
        if Matrix is not None:
            旋转矩阵 = Matrix.Rotation(旋转弧度, 4, "Z")
            对象.matrix_world @= 旋转矩阵
        else:
            对象.rotation_euler[2] = 旋转弧度

    # 分配材质
    if 材质 is None:
        材质 = 获取或创建发光材质(名称=名称, 颜色=颜色, 发光强度=发光强度)

    if 材质 is not None:
        if 对象.data.materials:
            对象.data.materials[0] = 材质
        else:
            对象.data.materials.append(材质)

        # 设置视图颜色
        try:
            对象.color = 颜色
            对象.active_material.diffuse_color = 颜色
        except (AttributeError, IndexError):
            pass

    return 对象


# --------------------------
# 场景清理函数
# --------------------------
def 清空场景(
    删除网格: bool = True,
    删除曲线: bool = True,
    删除材质: bool = False,
    清空缓存: bool = True,
) -> None:
    """
    优化的场景清理函数
    可选择性删除场景中的对象与数据
    """
    bpy = BlenderContext.get_bpy()
    if bpy is None:
        return

    # 删除所有对象
    for 对象 in list(bpy.context.scene.objects):
        bpy.data.objects.remove(对象, do_unlink=True)

    # 删除网格数据
    if 删除网格:
        for 网格 in list(bpy.data.meshes):
            bpy.data.meshes.remove(网格, do_unlink=True)

    # 删除曲线数据
    if 删除曲线:
        for 曲线 in list(bpy.data.curves):
            bpy.data.curves.remove(曲线, do_unlink=True)

    # 删除材质
    if 删除材质:
        for 材质项 in list(bpy.data.materials):
            bpy.data.materials.remove(材质项, do_unlink=True)

    # 清空材质缓存
    if 清空缓存:
        _材质缓存.clear()


# --------------------------
# 批量创建花朵
# --------------------------
def 创建花朵(
    花瓣性质: int = 6,
    花瓣数量: int = 6,
    外半径: float = 1.0,
    弧半径: float = 1.0,
    旋转角度: float = 0.0,
    中心坐标: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    采样点数: int = 4096,
    厚度: float = 0.01,
    颜色: Tuple[float, float, float, float] = (1.0, 0.5, 0.5, 1.0),
    线宽: int = 2,
    使用角度制=False,
) -> List[Any]:
    """批量创建完整花朵，一键生成所有花瓣"""
    花瓣列表 = []
    if 使用角度制 == False:
        角度步长 = 2 * np.pi / 花瓣数量
    else:
        角度步长 = 360 / 花瓣数量

    # 循环创建花瓣
    for i in range(花瓣数量):
        旋转 = i * 角度步长
        花瓣 = 创建花瓣(
            名称=f"花瓣_{i}",
            外半径=外半径,
            弧半径=弧半径,
            花瓣性质=花瓣性质,
            旋转角度=旋转 + 旋转角度,
            中心坐标=中心坐标,
            采样点数=采样点数,
            厚度=厚度,
            颜色=颜色,
            线宽=线宽,
            使用角度制=使用角度制,
        )
        花瓣列表.append(花瓣)

    return 花瓣列表


# --------------------------
# 运行示例
# --------------------------
if __name__ == "__main__":
    bpy = BlenderContext.get_bpy()
    if bpy is None:
        print("未检测到Blender环境，进入测试模式")
        测试弧线 = 计算花瓣弧线(外半径=1.0, 弧半径=1.05, 花瓣性质=5, 采样点数=1024)
        print(f"测试弧线形状: {测试弧线[0].shape}, {测试弧线[1].shape}")
    else:
        # 清空场景
        清空场景(删除材质=False)

        # 创建花朵
        花朵花瓣 = 创建花朵(
            花瓣性质=6,
            花瓣数量=6,
            外半径=1.0,
            弧半径=1.0,
            旋转角度=30,
            中心坐标=(0.0, 0.0, 1.0),
            采样点数=4096,
            厚度=0.01,
            颜色=(1.0, 0.5, 0.5, 1.0),
            线宽=2,
            使用角度制=True,
        )
        花朵花瓣 = 创建花朵(
            花瓣性质=4,
            花瓣数量=12,
            外半径=1.0,
            弧半径=1.0,
            旋转角度=15,
            中心坐标=(0.0, 0.0, 0),
            采样点数=4096,
            厚度=0.01,
            颜色=(1.0, 0.5, 0.5, 1.0),
            线宽=2,
            使用角度制=True,
        )
        print(f"成功创建 {len(花朵花瓣)} 个花瓣")
