# -*- coding: utf-8 -*-

import argparse
import os
import sys

import toml
import torch
import torch.nn as nn
import torch.nn.functional as F


class CONV_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()

        conv_class = nn.Conv1d if len(config["input_shape"]) == 3 else nn.Conv2d

        op_list = [
            conv_class(
                in_channels=config["in_channels"],
                out_channels=config["out_channels"],
                kernel_size=config["kernel_size"],
                stride=config["stride"],
                padding=config["padding"],
                dilation=config["dilation"],
                groups=config["groups"],
                bias=config["bias"],
            )
        ]
        if config["activation_func"] == "ReLU":
            op_list.append(nn.ReLU())
        self.ops = nn.Sequential(*op_list)
        self.config = config

    def forward(self, inputs):
        output = self.ops(inputs)
        return output


class LINEAR_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()

        op_list = [
            nn.Linear(
                in_features=config["in_features"],
                out_features=config["out_features"],
                bias=config["bias"],
            )
        ]
        if config["activation_func"] == "ReLU":
            op_list.append(nn.ReLU())
        self.ops = nn.Sequential(*op_list)
        self.config = config

    def forward(self, inputs):
        output = self.ops(inputs)
        return output


class ADD2D_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()

    def forward(self, input1, input2):
        output = input1 + input2
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class ADD_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()

        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = input0 + input1
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class SUB_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()

        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = input0 - input1
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class MUL2D_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()

    def forward(self, input1, input2):
        output = input1 * input2
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class MUL_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()

        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = input0 * input1
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class DIV_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()

        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = input0 / input1
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class EQUAL4D_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()

    def forward(self, input1, input2):
        output = torch.eq(input1, input2)
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class GLOBAL_AVERAGE_POOLING_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))

    def forward(self, input):
        return self.global_avg_pool(input)


class AVERAGE_POOLING_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.avg_pool = nn.AvgPool2d(
            kernel_size=config["kernel_size"],
            stride=config["stride"],
            padding=config["padding"],
        )

    def forward(self, input):
        return self.avg_pool(input)


class MAX_POOLING_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        c = self.config["input_shape"][1]
        self.pre_max_pool = nn.Sequential(
            nn.Conv2d(c, c, kernel_size=3, padding=1), nn.ReLU()
        )
        self.max_pool = nn.MaxPool2d(
            kernel_size=config["kernel_size"],
            stride=config["stride"],
            padding=config["padding"],
        )

    def forward(self, input):
        x = self.pre_max_pool(input)
        x = self.max_pool(x)
        return x


class RESIZE_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["conv"]:
            op_list = [
                nn.Conv2d(
                    in_channels=config["in_features"],
                    out_channels=config["out_features"],
                    kernel_size=[1, 1],
                    stride=[1, 1],
                    padding=[0, 0],
                    dilation=[1, 1],
                    groups=1,
                    bias=True,
                ),
                nn.Upsample(
                    size=(
                        tuple(config["size"])
                        if isinstance(config.get("size", None), list)
                        else config.get("size", None)
                    ),
                    scale_factor=(
                        tuple(config["scale_factor"])
                        if isinstance(config.get("scale_factor", None), list)
                        else config.get("scale_factor", None)
                    ),
                    mode=config["mode"],
                    align_corners=(
                        config["align_corners"] if config["align_corners"] else None
                    ),
                ),
            ]
        else:
            op_list = [
                nn.Upsample(
                    size=(
                        tuple(config["size"])
                        if isinstance(config.get("size", None), list)
                        else config.get("size", None)
                    ),
                    scale_factor=(
                        tuple(config["scale_factor"])
                        if isinstance(config.get("scale_factor", None), list)
                        else config.get("scale_factor", None)
                    ),
                    mode=config["mode"],
                    align_corners=(
                        config["align_corners"] if config["align_corners"] else None
                    ),
                )
            ]
        self.ops = nn.Sequential(*op_list)

    def forward(self, input):
        return self.ops(input)


class SIGMOID_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.sigmoid = nn.Sigmoid()

    def forward(self, input):
        return self.sigmoid(input)


class TANH_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.op = nn.Tanh()

    def forward(self, input):
        return self.op(input)


class RELU_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.op = nn.ReLU()

    def forward(self, input):
        return self.op(input)


class LEAKYRELU_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.op = nn.LeakyReLU(config["slope"])

    def forward(self, input):
        return self.op(input)


class PRELU_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.op = nn.PReLU(config["num_parameters"])

    def forward(self, input):
        return self.op(input)


class HARDSIGMOID_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.op = nn.Hardsigmoid()

    def forward(self, input):
        return self.op(input)


class HARDSWISH_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.op = nn.Hardswish()

    def forward(self, input):
        return self.op(input)


class CONCAT_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input1, input2):

        inputs = [input1, input2]
        if self.config.get("relu", False):
            relu_inputs = [nn.ReLU()(i) for i in inputs]
            inputs += relu_inputs

        return torch.cat(inputs, dim=self.config["axis"])


class CLIP_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, inputs):
        output = torch.clip(inputs, min=self.config["min"], max=self.config["max"])
        return output


class FLATTEN_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()

        self.flatten = nn.Flatten(config["start_dim"], config["end_dim"])
        self.config = config

    def forward(self, inputs):
        output = self.flatten(inputs)
        return output


class RESHAPE_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, inputs):
        output = torch.reshape(inputs, self.config["shape"])
        return output


class TRANSPOSE_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        return torch.permute(input, dims=self.config["perm"])


class SOFTMAX_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()

        self.op = nn.Softmax(config["dim"])
        self.config = config

    def forward(self, inputs):
        if self.config["relu"]:
            inputs = nn.ReLU()(inputs)
        output = self.op(inputs)
        return output


class SQUEEZE_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, inputs):
        if self.config["dim"]:
            output = torch.squeeze(inputs, self.config["dim"])
        else:
            output = torch.squeeze(inputs)
        return output


class UNSQUEEZE_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, inputs):
        output = torch.unsqueeze(inputs, self.config["dim"])
        return output


class EXP_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        return torch.exp(input)


class LOG_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        return torch.log(input)


class SQRT_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        return torch.sqrt(input)


class SLICE_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.starts = self.config["starts"]
        self.ends = self.config["ends"]
        self.axes = self.config["axes"]
        self.steps = self.config["steps"]
        self.flip = self.config.get("flip", 0)

    def forward(self, input):
        input = nn.ReLU()(input)
        if self.flip:
            output = torch.flip(input, self.axes)
        else:
            array_idx = []
            for i, dim in enumerate(input.shape):
                if i in self.axes:
                    index = self.axes.index(i)
                    array_idx.append(
                        slice(self.starts[index], self.ends[index], self.steps[index])
                    )
                else:
                    array_idx.append(slice(dim))
            output = input[array_idx]
        return output


class PAD_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.pads = [int(i) for i in self.config["pads"]]
        print(self.pads)

    def forward(self, input):
        input = nn.ReLU()(input)
        return F.pad(input, self.pads, self.config["mode"], self.config["const_value"])


class MATMUL_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["activation_func"] == "ReLU":
            self.act = nn.ReLU()
        if config["input1_is_weight"] and config["input_weight_shape"]:
            self.static_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, input1, *args):
        # By applying squeeze, the input is transformed to adapt the dimensions of matmul.
        input1 = torch.squeeze(input1, 0)
        input2 = None
        if len(args) > 0:
            input2 = args[0]
            input2 = torch.squeeze(input2, 0)
        elif hasattr(self, "static_weight"):
            input2 = self.static_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = torch.matmul(input1, input2)
        if hasattr(self, "act"):
            output = self.act(output)
        return output


class SPLIT_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        input = nn.ReLU()(input)
        output = torch.split(
            input, self.config["split_size_or_sections"], self.config["dim"]
        )
        return output


class GATHER_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.indices = torch.LongTensor(self.config["indices"])

    def forward(self, input):
        input = torch.squeeze(input, 0)
        array_idx = [
            self.indices if self.config["axis"] == i else slice(dim)
            for i, dim in enumerate(input.shape)
        ]
        output = input[array_idx]
        return output


class REQUANTIZE_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        amp = 0
        if self.config["shift_left"] == True:
            amp = 20

        input = nn.Sigmoid()(input) - 0.5
        input = input + amp
        output1 = (
            input[:, :, 0 : input.shape[2] // 2, 0 : input.shape[3] // 2]
            + input[:, :, input.shape[2] // 2 :, input.shape[3] // 2 :]
        )
        output2 = (
            input[:, :, 0 : input.shape[2] // 2, 0 : input.shape[3] // 2]
            - input[:, :, input.shape[2] // 2 :, input.shape[3] // 2 :]
        )
        output1 = output1 - 2 * amp
        output = torch.cat([output1, output2], dim=1)

        return output


class GREATER_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = torch.gt(input0, input1)
        return output


class GREATEROREQUAL_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = torch.ge(input0, input1)
        return output


class EQUAL_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = torch.eq(input0, input1)
        return output


class LESS_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = torch.lt(input0, input1)
        return output


class LESSOREQUAL_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        if config["input0_is_weight"] and config["input_weight_shape"]:
            self.input0_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )
        elif config["input1_is_weight"] and config["input_weight_shape"]:
            self.input1_weight = nn.Parameter(
                torch.randn(size=config["input_weight_shape"])
            )

    def forward(self, *args):
        input0 = None
        input1 = None
        if len(args) == 2:
            input0 = args[0]
            input1 = args[1]
        elif len(args) == 1 and hasattr(self, "input0_weight"):
            input0 = self.input0_weight
            input1 = args[0]
        elif len(args) == 1 and hasattr(self, "input1_weight"):
            input0 = args[0]
            input1 = self.input1_weight
        else:
            raise ValueError("Config of MatMul is error.")

        output = torch.le(input0, input1)
        return output


class ELU_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        output = nn.ELU(alpha=self.config["alpha"])(input)
        return output


class IDENTITY_TEST(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def forward(self, input):
        output = input
        return output


if __name__ == "__main__":
    print(f"Test {os.path.basename(sys.argv[0])} Module Start...")

    parser = argparse.ArgumentParser(description="Module Test")
    parser.add_argument(
        "-c", "--config", required=True, type=str, help="Config (*.toml)."
    )
    parser.add_argument(
        "-t", "--target", type=str, default="esp32p4", help="esp32p4 or esp32s3."
    )
    parser.add_argument(
        "-b", "--bits", type=int, default=8, help="the number of bits, support 8 or 16"
    )
    args = parser.parse_args()

    # get config
    config = toml.load(args.config)

    # get model
    conv_cfg = config["ops_test"]["Conv"]["cfg"][0]
    add2d_cfg = config["ops_test"]["add2d"]["cfg"][0]
    add2d_relu_cfg = config["ops_test"]["add2d"]["cfg"][1]
    mul2d_cfg = config["ops_test"]["mul2d"]["cfg"][0]
    mul2d_relu_cfg = config["ops_test"]["mul2d"]["cfg"][1]
    global_average_pooling_cfg = config["ops_test"]["global_average_pooling"]["cfg"][0]
    average_pooling_cfg = config["ops_test"]["average_pooling"]["cfg"][0]
    resize_cfg = config["ops_test"]["resize"]["cfg"][0]
    conv = CONV_TEST(conv_cfg)
    add2d = ADD2D_TEST(add2d_cfg)
    add2d_relu = ADD2D_TEST(add2d_relu_cfg)
    mul2d = MUL2D_TEST(mul2d_cfg)
    mul2d_relu = ADD2D_TEST(mul2d_relu_cfg)
    global_average_pooling = GLOBAL_AVERAGE_POOLING_TEST(global_average_pooling_cfg)
    average_pooling = AVERAGE_POOLING_TEST(average_pooling_cfg)
    resize = RESIZE_TEST(resize_cfg)

    # get inputs
    conv_inputs = torch.randn(conv_cfg["input_shape"])
    add2d_inputs = [
        torch.randn(add2d_cfg["input_shape"][0]),
        torch.randn(add2d_cfg["input_shape"][1]),
    ]
    mul2d_inputs = [
        torch.randn(mul2d_cfg["input_shape"][0]),
        torch.randn(mul2d_cfg["input_shape"][1]),
    ]
    global_average_pooling_inputs = torch.randn(
        global_average_pooling_cfg["input_shape"]
    )
    average_pooling_inputs = torch.randn(average_pooling_cfg["input_shape"])
    resize_inputs = torch.randn(resize_cfg["input_shape"])
    # print network
    # summary(conv, input_data=conv_inputs, col_names=("input_size", "output_size", "num_params"), device=torch.device('cpu'))
    # forward
    conv_outputs = conv(conv_inputs)
    add2d_outputs = add2d(*add2d_inputs)
    add2d_relu_outputs = add2d_relu(*add2d_inputs)
    mul2d_outputs = mul2d(*mul2d_inputs)
    mul2d_relu_outputs = mul2d_relu(*mul2d_inputs)
    global_average_pooling_outputs = global_average_pooling(
        global_average_pooling_inputs
    )
    average_pooling_outputs = average_pooling(average_pooling_inputs)
    resize_outputs = resize(resize_inputs)

    print(f"Test {os.path.basename(sys.argv[0])} Module End...")
    pass
