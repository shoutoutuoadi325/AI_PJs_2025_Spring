import os
import argparse
import numpy as np
import pandas as pd

from sklearn.preprocessing import label_binarize
from fea import feature_extraction
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from Bio.PDB import PDBParser


class LRModel:
    # todo:
    """
        Initialize Logistic Regression (from sklearn) model.

    """

    """
        Train the Logistic Regression model.

        Parameters:
        - train_data (array-like): Training data.
        - train_targets (array-like): Target values for the training data.
    """

    """
        Evaluate the performance of the Logistic Regression model.

        Parameters:
        - data (array-like): Data to be evaluated.
        - targets (array-like): True target values corresponding to the data.

        Returns:
        - float: Accuracy score of the model on the given data.
    """

    def __init__(self, C=100, max_iter=20000):
        self.model = LogisticRegression(C=C, max_iter=max_iter)

    def train(self, train_data, train_targets):
        self.scaler = StandardScaler()
        train_data = self.scaler.fit_transform(train_data)
        self.model.fit(train_data, train_targets)

    def evaluate(self, data, targets):
        data = self.scaler.transform(data)
        # y_pred = self.model.predict(data)
        # proba = self.model.predict_proba(data)
        return self.model.score(data, targets)


class LRFromScratch:
    # todo:
    def __init__(self, learning_rate=0.01, num_epochs=10000):
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.weights = None
        self.bias = None
#发现现象：学习率降低到0.001，迭代次数不变（100次），准确率反而降低了！此外，迭代次数从100增加为1000再增加为10000，准确率持续提升！
    def sigmoid(self, x):
        x = np.clip(x, -250, 250)
        return 1 / (1 + np.exp(-x))

    def train(self, train_data, train_targets):
        num_samples, num_features = train_data.shape
        self.weights = np.zeros(num_features)
        self.bias = 0
        # 梯度下降
        for _ in range(self.num_epochs):
            # 计算模型预测
            linear_model = np.dot(train_data, self.weights) + self.bias
            predictions = self.sigmoid(linear_model)

            # 计算梯度
            dw = (1 / num_samples) * np.dot(train_data.T, (predictions - train_targets))
            db = (1 / num_samples) * np.sum(predictions - train_targets)

            # 更新权重和偏置
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

    def predict(self, data):
        linear_model = np.dot(data, self.weights) + self.bias
        predictions = self.sigmoid(linear_model)
        return [1 if i > 0.5 else 0 for i in predictions]

    def evaluate(self, data, targets):
        predictions = self.predict(data)
        accuracy = np.mean(predictions == targets)
        return accuracy

def data_preprocess(args):
    if args.ent:
        diagrams = feature_extraction()[0]
    else:
        diagrams = np.load('./data/diagrams.npy')
    cast = pd.read_table('./data/SCOP40mini_sequence_minidatabase_19.cast')
    cast.columns.values[0] = 'protein'

    data_list = []
    target_list = []
    for task in range(1, 56):  # Assuming only one task for now
        task_col = cast.iloc[:, task]
        train_indices = (task_col==1) | (task_col==2)
        test_indices = (task_col==3) | (task_col==4)
        train_data = diagrams[train_indices]
        test_data = diagrams[test_indices]

        train_targets = (task_col[train_indices] == 1).astype(int)
        test_targets = (task_col[test_indices] == 3).astype(int)
        ## todo: Try to load data/target

        data_list.append((train_data, test_data))
        target_list.append((train_targets, test_targets))
    
    return data_list, target_list

def main(args):

    data_list, target_list = data_preprocess(args)

    task_acc_train = []
    task_acc_test = []
    

    #model = LRModel()
    model = LRFromScratch()

    for i in range(len(data_list)):
        train_data, test_data = data_list[i]
        train_targets, test_targets = target_list[i]

        print(f"Processing dataset {i+1}/{len(data_list)}")

        # Train the model
        model.train(train_data, train_targets)

        # Evaluate the model
        train_accuracy = model.evaluate(train_data, train_targets)
        test_accuracy = model.evaluate(test_data, test_targets)

        print(f"Dataset {i+1}/{len(data_list)} - Train Accuracy: {train_accuracy}, Test Accuracy: {test_accuracy}")

        task_acc_train.append(train_accuracy)
        task_acc_test.append(test_accuracy)


    print("Training accuracy:", sum(task_acc_train)/len(task_acc_train))
    print("Testing accuracy:", sum(task_acc_test)/len(task_acc_test))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LR Training and Evaluation")
    parser.add_argument('--ent', action='store_true', help="Load data from a file using a feature engineering function feature_extraction() from fea.py")
    args = parser.parse_args()
    main(args)

