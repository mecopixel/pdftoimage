from email.policy import default
from importlib.resources import path
import tkinter as tk            # ウィンドウ作成用
from tkinter import Variable, filedialog
from wsgiref.util import setup_testing_defaults  # ファイルを開くダイアログ用
from PIL import Image, ImageTk, ImageDraw, ImageFont  # 画像データ用
import numpy as np              # アフィン変換行列演算用
import os                       # ディレクトリ操作用
import cv2
from pathlib import Path
from pdf2image import convert_from_path
import PySimpleGUI as sg

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack() 
 
        self.pil_image = None           # 表示する画像データ
        self.my_title = "Image Viewer"  # タイトル
        self.back_color = "#008B8B"     # 背景色
        self.number = 1
        self.draw = None
        self.filename = None
        self.undos = []
        self.redos = []

        # ウィンドウの設定
        self.master.title(self.my_title)    # タイトル
        self.master.geometry("960x700")     # サイズ
 
        self.create_menu()   # メニューの作成
        self.create_widget() # ウィジェットの作成

        self.image_dir = Path("./image_file")

        if not os.path.exists(self.image_dir):
            # ディレクトリが存在しない場合、ディレクトリを作成する
            os.makedirs(self.image_dir)

    def menu_reset_clicked(self, event=None):
        self.number = 1

    def menu_numberset_clicked(self, event=None):
        layout =[[sg.InputText(default_text=1,size=(5,1),key='txt1'), sg.Button('OK',key='btn1')]]
        window = sg.Window('開始番号を入力', layout, size=(100,100))
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED: 
                break
            elif event == 'btn1':
                self.number = int(values['txt1'])
                break
        window.close()

    def menu_open_clicked(self, event=None):

        # ファイル→開く
        self.filename = tk.filedialog.askopenfilename(
            filetypes = [("all file", ".*")], # ファイルフィルタ
            initialdir = os.getcwd() # カレントディレクトリ
            )

        ext = os.path.splitext(os.path.basename(self.filename))[1]
        # PDFファイルのパス
        if ext == '.pdf':
            pdf_path = Path(self.filename)
            pages = convert_from_path(str(pdf_path), 200)
            for i, page in enumerate(pages):
                file_name = pdf_path.stem + "_{:02d}".format(i + 1) + ".jpg"
                image_path = self.image_dir / file_name
                page.save(str(image_path), "JPEG")
                if i == 0:
                    self.filename = Path("./" + str(image_path))
        # 画像ファイルを設定する
        self.set_image(self.filename)
    
    def menu_save_clicked(self, event=None):
        pil_pdf = self.pil_image.convert("RGB")
        # ファイル→保存
        self.pil_image.save("numbering_" + os.path.basename(self.filename))
        pil_pdf.save(os.path.splitext(os.path.basename(self.filename))[0] + ".pdf")

    def menu_newsave_clicked(self, event=None):
        # ファイル→保存
        filename = filedialog.asksaveasfilename()
        self.pil_image.save(filename)

    def set_undo(self, event=None):
        self.undos.append(self.pil_image.copy()) #undo_listの末尾に今のデータを追加   
        if len(self.undos)>20:
            self.undos.pop(0)

    def set_redo(self, event=None):
        self.redos.append(self.pil_image.copy())
        if len(self.redos)>20:
            self.redos.pop(0)

    def menu_undo_clicked(self, event=None):
        if not self.undos: #undo listが空の場合         
            return
        self.set_redo()
        self.pil_image = self.undos.pop(-1) #undo listから一番最後の値を取得し、削除する。
        self.number -= 1
        self.redraw_image()

    def menu_redo_clicked(self, event=None):
        if not self.redos: #undo listが空の場合         
            return
        self.set_undo()
        self.pil_image = self.redos.pop(-1) #undo listから一番最後の値を取得し、削除する。
        self.number += 1
        self.redraw_image()

    def menu_quit_clicked(self):
        # ウィンドウを閉じる
        self.master.destroy() 

    # create_menuメソッドを定義
    def create_menu(self):
        self.menu_bar = tk.Menu(self) # Menuクラスからmenu_barインスタンスを生成
 
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.font_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.number_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Font Size", menu=self.font_menu)
        self.menu_bar.add_cascade(label="NumberSet", menu=self.number_menu)

        self.fontsize = tk.IntVar() # ラジオボタンの値
        self.fontsize.set(32)
        ### 設定メニュー作成
        for i in range(26,55,2):
            self.font_menu.add_radiobutton(label=i, variable = self.fontsize, value=i)

        self.file_menu.add_command(label="Open", command = self.menu_open_clicked, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command = self.menu_save_clicked, accelerator="Ctrl+S")
        self.file_menu.add_command(label="New Save", command = self.menu_newsave_clicked, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Undo", command = self.menu_undo_clicked, accelerator="Ctrl+Z")
        self.file_menu.add_command(label="Redo", command = self.menu_redo_clicked, accelerator="Ctrl+Y")
        self.file_menu.add_command(label="Exit", command = self.menu_quit_clicked)

        self.number_menu.add_command(label="reset", command = self.menu_reset_clicked)
        self.number_menu.add_command(label="number set", command = self.menu_numberset_clicked)


        self.menu_bar.bind_all("<Control-o>", self.menu_open_clicked) # ファイルを開くのショートカット(Ctrol-Oボタン)
        self.menu_bar.bind_all("<Control-s>", self.menu_save_clicked) # ファイルを保存のショートカット(Ctrol-Sボタン)
        self.menu_bar.bind_all("<Control-z>", self.menu_undo_clicked) # 作業を戻すショートカット(Ctrol-Zボタン)
        self.menu_bar.bind_all("<Control-y>", self.menu_redo_clicked) # 作業を戻すショートカット(Ctrol-Yボタン)
        self.menu_bar.bind_all("<Control-n>", self.menu_newsave_clicked) # 作業を戻すショートカット(Ctrol-Nボタン)

        self.master.config(menu=self.menu_bar) # メニューバーの配置
 
    def create_widget(self):
        '''ウィジェットの作成'''

        # ステータスバー相当(親に追加)
        self.statusbar = tk.Frame(self.master)
        self.mouse_position = tk.Label(self.statusbar, relief = tk.SUNKEN, text="mouse position") # マウスの座標
        self.image_position = tk.Label(self.statusbar, relief = tk.SUNKEN, text="image position") # 画像の座標
        self.label_space = tk.Label(self.statusbar, relief = tk.SUNKEN)                           # 隙間を埋めるだけ
        self.image_info = tk.Label(self.statusbar, relief = tk.SUNKEN, text="image info")         # 画像情報
        self.mouse_position.pack(side=tk.LEFT)
        self.image_position.pack(side=tk.LEFT)
        self.label_space.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.image_info.pack(side=tk.RIGHT)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas
        self.canvas = tk.Canvas(self.master, background= self.back_color)
        self.canvas.pack(expand=True,  fill=tk.BOTH)  # この両方でDock.Fillと同じ

        # マウスイベント
        self.master.bind("<Motion>", self.mouse_move)                       # MouseMove
        self.master.bind("<B1-Motion>", self.mouse_move_left)               # MouseMove（左ボタンを押しながら移動）
        self.master.bind("<Button-1>", self.mouse_down_left)                # MouseDown（左ボタン）
        # self.master.bind("<Button-2>", self.mouse_down_right)                # MouseDown（右ボタン）
        self.master.bind("<Double-Button-1>", self.mouse_double_click_left) # MouseDoubleClick（左ボタン）
        self.master.bind("<MouseWheel>", self.mouse_wheel)                  # MouseWheel

    def set_image(self, filename):
        ''' 画像ファイルを開く '''
        if not filename:
            return
        # PIL.Imageで開く
        self.pil_image = Image.open(filename)
        # 画像全体に表示するようにアフィン変換行列を設定
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        # 画像の表示
        self.draw_image(self.pil_image)

        # ウィンドウタイトルのファイル名を設定
        self.master.title(self.my_title + " - " + os.path.basename(filename))
        # ステータスバーに画像情報を表示する
        self.image_info["text"] = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"
        # カレントディレクトリの設定
        os.chdir(os.path.dirname(filename))

    # -------------------------------------------------------------------------------
    # マウスイベント
    # -------------------------------------------------------------------------------

    def mouse_move(self, event):
        ''' マウスの移動時 '''
        # マウス座標
        self.mouse_position["text"] = f"mouse(x, y) = ({event.x: 4d}, {event.y: 4d})"
        if self.pil_image == None:
            return

        # 画像座標
        mouse_posi = np.array([event.x, event.y, 1]) # マウス座標(numpyのベクトル)
        mat_inv = np.linalg.inv(self.mat_affine)     # 逆行列（画像→Cancasの変換からCanvas→画像の変換へ）
        image_posi = np.dot(mat_inv, mouse_posi)     # 座標のアフィン変換
        x = int(np.floor(image_posi[0]))
        y = int(np.floor(image_posi[1]))
        if x >= 0 and x < self.pil_image.width and y >= 0 and y < self.pil_image.height:
            # 輝度値の取得
            value = self.pil_image.getpixel((x, y))
            self.image_position["text"] = f"image({x: 4d}, {y: 4d}) = {value}"
        else:
            self.image_position["text"] = "-------------------------"

    def mouse_move_left(self, event):
        ''' マウスの左ボタンをドラッグ '''
        if self.pil_image == None:
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image() # 再描画
        self.__old_event = event

    def mouse_down_left(self, event):
        ''' マウスの左ボタンを押した '''
        if self.pil_image == None:
            return
        
        self.redraw_image() # 再描画
        self.__old_event = event

    def mouse_down_right(self, event):

        '''マウスの右ボタンを押した'''
        self.set_undo()
        if self.pil_image == None:
            return
        
        self.draw = ImageDraw.Draw(self.pil_image)
        mouse_posi = np.array([event.x, event.y, 1]) # マウス座標(numpyのベクトル)
        mat_inv = np.linalg.inv(self.mat_affine)     # 逆行列（画像→Cancasの変換からCanvas→画像の変換へ）
        image_posi = np.dot(mat_inv, mouse_posi)     # 座標のアフィン変換
        x = int(np.floor(image_posi[0]))
        y = int(np.floor(image_posi[1]))
        self.draw.line()
        self.redraw_image() # 再描画

    def mouse_double_click_left(self, event):
        ''' マウスの左ボタンをダブルクリック '''
        self.set_undo()
        if self.pil_image == None:
            return
        # self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.draw = ImageDraw.Draw(self.pil_image)
        # 画像座標
        mouse_posi = np.array([event.x, event.y, 1]) # マウス座標(numpyのベクトル)
        mat_inv = np.linalg.inv(self.mat_affine)     # 逆行列（画像→Cancasの変換からCanvas→画像の変換へ）
        image_posi = np.dot(mat_inv, mouse_posi)     # 座標のアフィン変換
        x = int(np.floor(image_posi[0]))
        y = int(np.floor(image_posi[1])) 
        font = ImageFont.truetype("arial.ttf", size=self.fontsize.get())
        if self.number < 0:
            self.number = 1 # ０以下にならないように
        self.draw.text(
            (x,y),
            str(self.number),
            font = font,
            fill = 'red',
            anchor = 'mm'
        )
        self.number += 1
        self.redraw_image() # 再描画

    def mouse_wheel(self, event):
        ''' マウスホイールを回した '''
        if self.pil_image == None:
            return

        if (event.delta < 0):
            # 上に回転の場合、縮小
            self.scale_at(0.8, event.x, event.y)
        else:
            # 下に回転の場合、拡大
            self.scale_at(1.25, event.x, event.y)
        
        self.redraw_image() # 再描画

    # -------------------------------------------------------------------------------
    # 画像表示用アフィン変換
    # -------------------------------------------------------------------------------

    def reset_transform(self):
        '''アフィン変換を初期化（スケール１、移動なし）に戻す'''
        self.mat_affine = np.eye(3) # 3x3の単位行列

    def translate(self, offset_x, offset_y):
        ''' 平行移動 '''
        mat = np.eye(3) # 3x3の単位行列
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale:float):
        ''' 拡大縮小 '''
        mat = np.eye(3) # 単位行列
        mat[0, 0] = scale
        mat[1, 1] = scale

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale:float, cx:float, cy:float):
        ''' 座標(cx, cy)を中心に拡大縮小 '''

        # 原点へ移動
        self.translate(-cx, -cy)
        # 拡大縮小
        self.scale(scale)
        # 元に戻す
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):
        '''画像をウィジェット全体に表示させる'''

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        # アフィン変換の初期化
        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            # ウィジェットが横長（画像を縦に合わせる）
            scale = canvas_height / image_height
            # あまり部分の半分を中央に寄せる
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            # ウィジェットが縦長（画像を横に合わせる）
            scale = canvas_width / image_width
            # あまり部分の半分を中央に寄せる
            offsety = (canvas_height - image_height * scale) / 2

        # 拡大縮小
        self.scale(scale)
        # あまり部分を中央に寄せる
        self.translate(offsetx, offsety)

    # -------------------------------------------------------------------------------
    # 描画
    # -------------------------------------------------------------------------------

    def draw_image(self, pil_image):
        
        if pil_image == None:
            return
        
        self.canvas.delete("all")

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # キャンバスから画像データへのアフィン変換行列を求める
        #（表示用アフィン変換行列の逆行列を求める）
        mat_inv = np.linalg.inv(self.mat_affine)

        # PILの画像データをアフィン変換する
        dst = pil_image.transform(
                    (canvas_width, canvas_height),  # 出力サイズ
                    Image.AFFINE,                   # アフィン変換
                    tuple(mat_inv.flatten()),       # アフィン変換行列（出力→入力への変換行列）を一次元のタプルへ変換
                    Image.NEAREST,                  # 補間方法、ニアレストネイバー 
                    fillcolor= self.back_color
                    )

        # 表示用画像を保持
        self.image = ImageTk.PhotoImage(image=dst)

        # 画像の描画
        self.canvas.create_image(
                0, 0,               # 画像表示位置(左上の座標)
                anchor='nw',        # アンカー、左上が原点
                image=self.image    # 表示画像データ
                )

    def redraw_image(self):
        ''' 画像の再描画 '''
        if self.pil_image == None:
            return
        self.draw_image(self.pil_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()