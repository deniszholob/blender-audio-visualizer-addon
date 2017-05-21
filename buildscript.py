import os
import shutil

dev_addon_dir = "./add_dz_visualiser"
blender_addon_dir = "./build/blender-2.78c-windows64/2.78/scripts/addons/add_dz-visualiser"

# Go through the source directory
# create any directories that do not already exist in destination directory, 
# and move files from source to the destination directory:
# Source: http://stackoverflow.com/questions/7419665/python-move-and-overwrite-files-and-folders
def copyAddonToBlender(root_src_dir, root_dst_dir):
    """ Copies the addon to blenders addon directory """
    checkSrcDir(root_src_dir)
    checkDestDir(root_dst_dir)
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            # if os.path.exists(dst_file):
            #     os.remove(dst_file)
            shutil.copy(src_file, dst_dir)
            print("Adding " + dst_file)
# End fnc


def checkSrcDir(root_src_dir):
    if not os.path.exists(root_src_dir):
        print("Source dir doesnt exists: " + root_src_dir)
# End fnc


def checkDestDir(root_dst_dir):
    if not os.path.exists(root_dst_dir):
        os.makedirs(root_dst_dir)
# End fnc


def main():
    """Main function"""
    copyAddonToBlender(dev_addon_dir, blender_addon_dir)
# End fnc


if __name__ == '__main__':
    main()
# End if
