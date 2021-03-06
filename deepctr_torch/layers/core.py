import torch
import torch.nn as nn
import torch.nn.functional as F


class DNN(nn.Module):
    def __init__(self, inputs_dim, hidden_units, activation=F.relu, l2_reg=0, dropout_rate=0, use_bn=False,
                 init_std=0.0001, seed=1024):
        super(DNN, self).__init__()
        self.activation = activation
        self.dropout_rate = dropout_rate
        self.dropout = nn.Dropout(dropout_rate)
        self.seed = seed
        self.l2_reg = l2_reg
        self.use_bn = use_bn
        hidden_units = [inputs_dim] + list(hidden_units)
        self.linears = nn.ModuleList(
            [nn.Linear(hidden_units[i], hidden_units[i + 1]) for i in range(len(hidden_units) - 1)])
        for tensor in self.linears:
            nn.init.normal_(tensor.weight, mean=0, std=init_std)

    def forward(self, inputs):
        deep_input = inputs

        for i in range(len(self.linears)):
            fc = self.linears[i](deep_input)

            # if self.use_bn:
            #    fc = self.bn_layers[i](fc, training=training)

            fc = self.activation(fc)

            fc = self.dropout(fc)
            deep_input = fc
        return deep_input


class PredictionLayer(nn.Module):
    """
      Arguments
         - **task**: str, ``"binary"`` for  binary logloss or  ``"regression"`` for regression loss
         - **use_bias**: bool.Whether add bias term or not.
    """

    def __init__(self, task='binary', use_bias=True, **kwargs):
        if task not in ["binary", "multiclass", "regression"]:
            raise ValueError("task must be binary,multiclass or regression")

        super(PredictionLayer, self).__init__()
        self.use_bias = use_bias
        self.task = task
        if self.use_bias:
            self.global_bias = nn.Parameter(torch.zeros((1,)))

    def forward(self, X):
        output = X
        if self.use_bias:
            output += self.global_bias
        if self.task == "binary":
            output = torch.sigmoid(output)
        return output
