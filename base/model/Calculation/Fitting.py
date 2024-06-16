import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import skewnorm


class Fitting:
    def __init__(self):
        self.x = None
        self.y = None
        self.functions = {  # name: (func, color)
            'Quadratic': (self.poly2, 'red'),
            'Cubic': (self.poly3, 'blue'),
            'Sinusoidal': (self.sin_func, 'green'),
            'Gaussian': (self.gaussian, 'magenta'),
            'Lorentzian': (self.lorentzian, 'cyan'),
            'Asymmetric Gaussian': (self.asymmetric_gaussian, 'orange'),
            'Skewed Gaussian': (self.skewed_gaussian, 'purple')
        }
        self.init_params = {
            'Quadratic': [1, 1, 1],  # a, b, c
            'Cubic': [1, 1, 1, 1],  # a, b, c, d
            'Sinusoidal': [1, 0.01, 0, 0],  # A, B, C, D
            'Gaussian': [1, 0, 50],  # A, mu, sigma
            'Lorentzian': [1, 0, 50],  # A, x0, gamma
            'Asymmetric Gaussian': [1, 0, 50, 30],  # A, mu, sigma_l, sigma_r
            'Skewed Gaussian': [1, 0, 50, -5]  # A, mu, sigma, alpha
        }
        # 作った時に、使える関数が表示されるようにする
        for i, item in enumerate(self.functions):
            print(f"{i + 1}: {item}")

    # 使える関数一覧を表示
    def display_functions(self):
        for i, item in enumerate(self.functions):
            print(f"{i + 1}: {item}")

    # データの設定
    def set_data(self, x, y):
        self.x = x
        self.y = y

    # 初期値の変更
    def change_init_params(self, option):
        if option == 'spe':
            # speデータは一つの極大をもつのでそれを想定
            # sin
            adjusted_period = 2 * (self.x.max() - self.x.min())
            self.init_params['Sinusoidal'][0] = self.x.max() - self.x.min()
            self.init_params['Sinusoidal'][1] = 2 * np.pi / adjusted_period
            self.init_params['Sinusoidal'][3] = np.mean(self.y)
            # gaussian
            self.init_params['Gaussian'][0] = max(self.y)
            self.init_params['Gaussian'][1] = np.mean(self.x)
            # lorentzian
            self.init_params['Lorentzian'][0] = max(self.y)
            self.init_params['Lorentzian'][1] = np.mean(self.x)
            # 非対称gausian
            self.init_params['Asymmetric Gaussian'][0] = max(self.y)
            self.init_params['Asymmetric Gaussian'][1] = np.mean(self.x)
            self.init_params['Skewed Gaussian'][0] = max(self.y)
            self.init_params['Skewed Gaussian'][1] = np.mean(self.x)
        if option == 'xrd':
            print('to be planned...')
        print('')
        for i, key in enumerate(self.init_params):
            print(f"{key: <20} -> {self.init_params[key]}")
        print("") # 次と1行空ける用

    def fit_and_plot_all(self):
        rss_values = {}

        plt.figure(figsize=(12, 8))
        plt.scatter(self.x, self.y, label='Original Data', color='lightgrey')
        for name, (func, color) in self.functions.items():
            popt, _ = curve_fit(func, self.x, self.y, p0=self.init_params[name])
            y_pred = func(self.x, *popt)
            rss = np.sum((self.y - y_pred) ** 2)
            rss_values[name] = round(rss)
            plt.plot(self.x, y_pred, label=f'{name} Fit: RSS={rss:.2f}', color=color)

        # 残差平方和を出力する
        sorted_rss = sorted(rss_values.items(), key=lambda item: item[1])
        print("RSSの低い順(整数で丸めてる):")
        for name, rss in sorted_rss:
            print(f"{name: <20}: RSS={rss: >12}")

        plt.title('Data Fitting Comparison')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.show()

    def fit_specific_function(self, *,
                              function_name):
        if function_name in self.functions:
            func, _ = self.functions[function_name]
            popt, pcov = curve_fit(func, self.x, self.y, p0=self.init_params[function_name])
            perr = np.sqrt(np.diag(pcov))  # パラメータの標準偏差を計算する
            return popt, perr
        else:
            raise ValueError(f"No function named {function_name} found.")

    # fitting関数一覧。ここを変更する場合は__init__処理のfuntions辞書も変更が必要
    def poly2(self, x, a, b, c):
        return a * x ** 2 + b * x + c

    def poly3(self, x, a, b, c, d):
        return a * x ** 3 + b * x ** 2 + c * x + d

    def sin_func(self, x, A, B, C, D):
        return A * np.sin(B * x + C) + D

    def gaussian(self, x, A, mu, sigma):
        return A * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))

    def lorentzian(self, x, A, x0, gamma):
        return A * gamma ** 2 / ((x - x0) ** 2 + gamma ** 2)

    def asymmetric_gaussian(self, x, A, mu, sigma_l, sigma_r):
        return np.where(x < mu, A * np.exp(-(x - mu) ** 2 / (2 * sigma_l ** 2)),
                        A * np.exp(-(x - mu) ** 2 / (2 * sigma_r ** 2)))

    def skewed_gaussian(self, x, A, mu, sigma, alpha):
        return A * skewnorm.pdf(x, alpha, loc=mu, scale=sigma)

    # LogNormalも実装してみる


"""
Example usage:
"""
# FIXME 修正いるかも
# インスタンス作成
# fitting = Fitting()
# fitting.set_data(x_data, y_data)

# いろんな関数でfittingして比較する
# fitting.fit_and_plot_all()

# 特定の関数でfittingする
# popt = fitting.fit_specific_function('Gaussian')
# print("Fitting parameters:", popt)
