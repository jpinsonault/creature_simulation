import pyopencl as cl

for platform in cl.get_platforms():
    for device in platform.get_devices():
        print("===============================================================")
        print("Platform name: {}".format(platform.name))
        print("Platform profile: {}".format(platform.profile))
        print("Platform vendor: {}".format(platform.vendor))
        print("Platform version: {}".format(platform.version))
        print("---------------------------------------------------------------")
        print("Device name: {}".format(device.name))
        print("Device type: {}".format(cl.device_type.to_string(device.type)))
        print("Memory: {}{}".format(device.global_mem_size//1024//1024, 'MB'))
        print("Max clock speed: {}{}".format(device.max_clock_frequency, 'MHz'))
        print("Compute units: {}".format(device.max_compute_units))
        print("Max work item size: {}".format(device.max_work_item_sizes))
        print("Max work group size: {}".format(device.max_work_group_size))
        # print("Device extensions: {}".format("\n".join(device.extensions.split(" "))))
