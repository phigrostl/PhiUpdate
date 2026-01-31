import apkutils
import xml.etree.ElementTree as ET

def get_apk_version(apk_path):
    """
    解析APK文件，获取versionName和versionCode（适配新版apkutils，处理XML字符串返回值）
    :param apk_path: APK文件的路径（绝对路径/相对路径）
    :return: 字典格式，包含versionName、versionCode、packageName
    """
    try:
        # 步骤1：新版apkutils通过from_file()方法加载APK文件
        apk = apkutils.APK.from_file(apk_path)
        
        # 步骤2：获取XML格式的字符串（新版返回值为XML字符串，而非字典）
        manifest_xml_str = apk.get_manifest()
        if not manifest_xml_str:
            return "错误：未能提取到AndroidManifest.xml内容"
        
        # 步骤3：解析XML字符串，提取核心信息
        # 解析XML根节点
        root = ET.fromstring(manifest_xml_str)
        
        # 定义Android命名空间（必须指定，否则无法获取属性值）
        android_ns = {"android": "http://schemas.android.com/apk/res/android"}
        
        # 提取版本信息和包名（从XML根节点<manifest>中获取）
        package_name = root.get("package", "未知包名")
        version_name = root.get("android:versionName", "未知版本名称")
        # 若通过get直接获取失败，用findtext（兼容部分特殊APK格式）
        if version_name == "未知版本名称":
            version_name = root.get("{" + android_ns["android"] + "}versionName", "未知版本名称")
        
        version_code = root.get("android:versionCode", "未知版本号")
        if version_code == "未知版本号":
            version_code = root.get("{" + android_ns["android"] + "}versionCode", "未知版本号")
        
        return {
            "packageName": package_name,
            "versionName": version_name,
            "versionCode": version_code
        }
    
    except FileNotFoundError:
        return f"错误：未找到APK文件，请检查路径是否正确：{apk_path}"
    except Exception as e:
        return f"错误：解析APK失败，原因：{str(e)}"

# 测试使用（替换为你的APK文件路径）
if __name__ == "__main__":
    apk_file_path = "3.18.2.apk"  # 你的APK文件路径
    version_info = get_apk_version(apk_file_path)
    print("APK版本信息：")
    if isinstance(version_info, dict):
        for key, value in version_info.items():
            print(f"{key}: {value}")
    else:
        print(version_info)