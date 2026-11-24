
import tkinter as tk
from tkinter import filedialog, messagebox
import math
import csv
import time


BG = "#0B1020"
PANEL = "#121A2B"
CARD = "#18243A"
BLUE = "#2589FF"
CYAN = "#21D4FD"
WHITE = "#F1F5F9"
MUTED = "#94A3B8"
GREEN = "#20C997"
ORANGE = "#FFB454"


class DaviaPhysicsLab:

    def __init__(self, root):
        self.root = root
        self.root.title("davIA Physics Lab 2.0")
        self.root.geometry("1200x760")
        self.root.minsize(950, 650)
        self.root.configure(bg=BG)

        self.length = tk.DoubleVar(value=1.0)
        self.angle = tk.DoubleVar(value=25.0)
        self.gravity = tk.DoubleVar(value=9.81)
        self.damping = tk.DoubleVar(value=0.05)

        self.t = 0.0
        self.theta = math.radians(self.angle.get())
        self.omega = 0.0

        self.data = []
        self.running = False
        self.after_id = None
        self.last_tick = None
        self.accumulator = 0.0
        self.step = 0.01

        self.create_interface()
        self.update_values()
        self.draw_pendulum()
        self.draw_graph()

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    # ---------------- INTERFACE ----------------

    def create_interface(self):

        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=12)

        tk.Label(
            header,
            text="davIA",
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        tk.Label(
            header,
            text="PHYSICS LAB 2.0",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=12, pady=10)

        tk.Label(
            header,
            text="LABORATÓRIO VIRTUAL DE FÍSICA",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(side="right")

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=8)

        self.sidebar = tk.Frame(
            main, bg=PANEL, width=240
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 12))
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="EXPERIMENTOS",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=15, pady=15)

        tk.Label(
            self.sidebar,
            text="●  Pêndulo simples",
            bg=CARD,
            fg=CYAN,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=12
        ).pack(fill="x", padx=8)

        for name in [
            "Queda livre",
            "Lançamento oblíquo",
            "Movimento harmônico",
            "Eletricidade",
            "Lei de Hooke"
        ]:
            tk.Label(
                self.sidebar,
                text="   " + name,
                bg=PANEL,
                fg=WHITE,
                font=("Segoe UI", 10),
                anchor="w",
                padx=12,
                pady=12
            ).pack(fill="x", padx=8)

        tk.Label(
            self.sidebar,
            text="PARÂMETROS",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=15, pady=(20, 10))

        self.add_control(
            "Comprimento (m)", self.length, 0.2, 3.0
        )
        self.add_control(
            "Ângulo inicial (°)", self.angle, 1, 80
        )
        self.add_control(
            "Gravidade (m/s²)", self.gravity, 1, 20
        )
        self.add_control(
            "Amortecimento", self.damping, 0, 1
        )

        self.content = tk.Frame(main, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        metrics = tk.Frame(self.content, bg=BG)
        metrics.pack(fill="x", pady=(0, 10))

        self.period_label = self.metric(
            metrics, "PERÍODO", "0.00 s"
        )
        self.time_label = self.metric(
            metrics, "TEMPO", "0.00 s"
        )
        self.angle_label = self.metric(
            metrics, "ÂNGULO", "0.00°"
        )
        self.speed_label = self.metric(
            metrics, "VELOCIDADE ANGULAR", "0.00 rad/s"
        )

        visual = tk.Frame(self.content, bg=BG)
        visual.pack(fill="both", expand=True)

        pendulum_panel = tk.Frame(visual, bg=PANEL)
        pendulum_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 6)
        )

        graph_panel = tk.Frame(visual, bg=PANEL)
        graph_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(6, 0)
        )

        tk.Label(
            pendulum_panel,
            text="ANIMAÇÃO DO PÊNDULO",
            bg=PANEL,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=12)

        self.pendulum_canvas = tk.Canvas(
            pendulum_panel,
            bg="#0E1729",
            highlightthickness=0
        )
        self.pendulum_canvas.pack(
            fill="both", expand=True, padx=10, pady=(0, 10)
        )
        self.pendulum_canvas.bind(
            "<Configure>",
            lambda event: self.draw_pendulum()
        )

        tk.Label(
            graph_panel,
            text="GRÁFICO: ÂNGULO × TEMPO",
            bg=PANEL,
            fg=WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=12)

        self.graph_canvas = tk.Canvas(
            graph_panel,
            bg="#0E1729",
            highlightthickness=0
        )
        self.graph_canvas.pack(
            fill="both", expand=True, padx=10, pady=(0, 10)
        )
        self.graph_canvas.bind(
            "<Configure>",
            lambda event: self.draw_graph()
        )

        buttons = tk.Frame(self.content, bg=BG)
        buttons.pack(fill="x", pady=12)

        self.make_button(
            buttons, "INICIAR", GREEN, self.start
        )
        self.make_button(
            buttons, "PAUSAR", ORANGE, self.pause
        )
        self.make_button(
            buttons, "REINICIAR", BLUE, self.reset
        )
        self.make_button(
            buttons, "EXPORTAR CSV", CYAN, self.export_csv
        )
        self.make_button(
            buttons, "SALVAR EXPERIMENTO",
            "#A78BFA", self.save_experiment
        )

    def add_control(self, title, variable, minimum, maximum):

        frame = tk.Frame(self.sidebar, bg=PANEL)
        frame.pack(fill="x", padx=12, pady=5)

        tk.Label(
            frame,
            text=title,
            bg=PANEL,
            fg=WHITE,
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        value_label = tk.Label(
            frame,
            text=f"{variable.get():.2f}",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 9, "bold")
        )
        value_label.pack(anchor="e")

        def changed(value):
            value_label.config(text=f"{float(value):.2f}")
            if not self.running:
                self.draw_pendulum()
                self.update_values()

        tk.Scale(
            frame,
            variable=variable,
            from_=minimum,
            to=maximum,
            resolution=0.01,
            orient="horizontal",
            showvalue=False,
            bg=PANEL,
            fg=WHITE,
            troughcolor=CARD,
            highlightthickness=0,
            command=changed
        ).pack(fill="x")

        entry = tk.Entry(
            frame,
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat"
        )
        entry.insert(0, str(variable.get()))
        entry.pack(fill="x", pady=(2, 5))

        def apply_value(event=None):
            try:
                value = float(entry.get().replace(",", "."))
                value = max(minimum, min(maximum, value))
                variable.set(value)
                value_label.config(text=f"{value:.2f}")
                entry.delete(0, "end")
                entry.insert(0, str(value))

                if not self.running:
                    self.draw_pendulum()
                    self.update_values()

            except ValueError:
                messagebox.showwarning(
                    "Valor inválido",
                    "Digite um número válido."
                )
                entry.delete(0, "end")
                entry.insert(0, str(variable.get()))

        entry.bind("<Return>", apply_value)
        entry.bind("<FocusOut>", apply_value)

    def metric(self, parent, title, value):

        card = tk.Frame(parent, bg=CARD, padx=10, pady=10)
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=3
        )

        tk.Label(
            card,
            text=title,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        label = tk.Label(
            card,
            text=value,
            bg=CARD,
            fg=CYAN,
            font=("Segoe UI", 13, "bold")
        )
        label.pack(anchor="w", pady=(5, 0))

        return label

    def make_button(self, parent, text, color, command):

        tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#08111F",
            activebackground=color,
            relief="flat",
            bd=0,
            padx=8,
            pady=11,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2"
        ).pack(
            side="left",
            padx=3,
            fill="x",
            expand=True
        )

    # ---------------- FÍSICA ----------------

    def period(self):
        return 2 * math.pi * math.sqrt(
            self.length.get() / self.gravity.get()
        )

    def acceleration(self, theta, omega):
        return (
            -(self.gravity.get() / self.length.get())
            * math.sin(theta)
            - self.damping.get() * omega
        )

    def rk4(self, h):

        a1 = self.acceleration(self.theta, self.omega)
        b1 = self.omega

        a2 = self.acceleration(
            self.theta + b1 * h / 2,
            self.omega + a1 * h / 2
        )
        b2 = self.omega + a1 * h / 2

        a3 = self.acceleration(
            self.theta + b2 * h / 2,
            self.omega + a2 * h / 2
        )
        b3 = self.omega + a2 * h / 2

        a4 = self.acceleration(
            self.theta + b3 * h,
            self.omega + a3 * h
        )
        b4 = self.omega + a3 * h

        self.theta += h * (
            b1 + 2*b2 + 2*b3 + b4
        ) / 6

        self.omega += h * (
            a1 + 2*a2 + 2*a3 + a4
        ) / 6

        self.t += h

    def update_values(self):

        self.period_label.config(
            text=f"{self.period():.3f} s"
        )
        self.time_label.config(
            text=f"{self.t:.2f} s"
        )
        self.angle_label.config(
            text=f"{math.degrees(self.theta):.2f}°"
        )
        self.speed_label.config(
            text=f"{self.omega:.3f} rad/s"
        )

    # ---------------- PÊNDULO ----------------

    def draw_pendulum(self):

        if not hasattr(self, "pendulum_canvas"):
            return

        canvas = self.pendulum_canvas
        canvas.delete("all")

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 50 or height < 50:
            return

        px = width / 2
        py = 50

        scale = min(width * 0.35, height * 0.60)
        radius = self.length.get() * scale

        bx = px + radius * math.sin(self.theta)
        by = py + radius * math.cos(self.theta)

        canvas.create_line(
            px - 35, py,
            px + 35, py,
            fill=MUTED,
            width=5
        )

        canvas.create_line(
            px, py, bx, by,
            fill=CYAN,
            width=3
        )

        canvas.create_oval(
            px - 6, py - 6,
            px + 6, py + 6,
            fill=WHITE,
            outline=""
        )

        canvas.create_oval(
            bx - 17, by - 17,
            bx + 17, by + 17,
            fill=BLUE,
            outline=CYAN,
            width=2
        )

        canvas.create_text(
            12, height - 15,
            text=f"L = {self.length.get():.2f} m",
            fill=MUTED,
            anchor="w"
        )

    # ---------------- GRÁFICO ----------------

    def draw_graph(self):

        if not hasattr(self, "graph_canvas"):
            return

        canvas = self.graph_canvas
        canvas.delete("all")

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 60 or height < 60:
            return

        left = 48
        right = width - 15
        top = 25
        bottom = height - 42

        canvas.create_line(
            left, top, left, bottom,
            fill=MUTED
        )

        canvas.create_line(
            left, bottom, right, bottom,
            fill=MUTED
        )

        for degree in [-80, -40, 0, 40, 80]:

            y = bottom - (
                (degree + 90) / 180
            ) * (bottom - top)

            canvas.create_line(
                left, y, right, y,
                fill="#26364D",
                dash=(2, 4)
            )

            canvas.create_text(
                left - 7, y,
                text=str(degree),
                fill=MUTED,
                anchor="e",
                font=("Segoe UI", 8)
            )

        canvas.create_text(
            (left + right) / 2,
            height - 12,
            text="Tempo (s)",
            fill=WHITE,
            font=("Segoe UI", 9)
        )

        if len(self.data) < 2:
            canvas.create_text(
                (left + right) / 2,
                (top + bottom) / 2,
                text="Inicie para gerar o gráfico",
                fill=MUTED
            )
            return

        visible = self.data[-1000:]
        start_t = visible[0][0]
        end_t = visible[-1][0]
        duration = max(end_t - start_t, 0.01)

        points = []

        for t, angle, omega in visible:

            x = left + (
                (t - start_t) / duration
            ) * (right - left)

            y = bottom - (
                (angle + 90) / 180
            ) * (bottom - top)

            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(
                *points,
                fill=CYAN,
                width=2
            )

    # ---------------- SIMULAÇÃO ----------------

    def start(self):

        if self.running:
            return

        self.running = True
        self.last_tick = time.perf_counter()
        self.accumulator = 0.0
        self.animate()

    def animate(self):

        if not self.running:
            return

        now = time.perf_counter()
        elapsed = min(now - self.last_tick, 0.1)
        self.last_tick = now

        self.accumulator += elapsed

        while self.accumulator >= self.step:

            self.rk4(self.step)
            self.accumulator -= self.step

            self.data.append((
                self.t,
                math.degrees(self.theta),
                self.omega
            ))

        self.update_values()
        self.draw_pendulum()
        self.draw_graph()

        self.after_id = self.root.after(
            20, self.animate
        )

    def pause(self):

        self.running = False

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def reset(self):

        self.pause()

        self.t = 0.0
        self.theta = math.radians(self.angle.get())
        self.omega = 0.0
        self.data = []
        self.accumulator = 0.0

        self.update_values()
        self.draw_pendulum()
        self.draw_graph()

    # ---------------- SALVAR ARQUIVOS ----------------

    def export_csv(self):

        if not self.data:
            messagebox.showinfo(
                "Sem dados",
                "Inicie o experimento antes de exportar."
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            initialfile="davia_pendulo_dados.csv"
        )

        if not path:
            return

        try:
            with open(
                path, "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file, delimiter=";")

                writer.writerow([
                    "Tempo (s)",
                    "Ângulo (graus)",
                    "Velocidade angular (rad/s)"
                ])

                writer.writerows(self.data)

            messagebox.showinfo(
                "Sucesso",
                "Dados exportados para CSV."
            )

        except OSError as error:
            messagebox.showerror("Erro", str(error))

    def save_experiment(self):

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            initialfile="davia_experimento_pendulo.csv"
        )

        if not path:
            return

        try:
            with open(
                path, "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file, delimiter=";")

                writer.writerow(["DAVIA PHYSICS LAB 2.0"])
                writer.writerow([
                    "Experimento", "Pêndulo simples"
                ])
                writer.writerow([
                    "Data",
                    time.strftime("%d/%m/%Y %H:%M:%S")
                ])

                writer.writerow([])
                writer.writerow(["PARÂMETROS"])

                writer.writerow([
                    "Comprimento (m)", self.length.get()
                ])
                writer.writerow([
                    "Ângulo inicial (graus)", self.angle.get()
                ])
                writer.writerow([
                    "Gravidade (m/s²)", self.gravity.get()
                ])
                writer.writerow([
                    "Amortecimento", self.damping.get()
                ])
                writer.writerow([
                    "Período teórico (s)", self.period()
                ])

                writer.writerow([])
                writer.writerow(["DADOS DA SIMULAÇÃO"])

                writer.writerow([
                    "Tempo (s)",
                    "Ângulo (graus)",
                    "Velocidade angular (rad/s)"
                ])

                writer.writerows(self.data)

            messagebox.showinfo(
                "Experimento salvo",
                "Parâmetros e dados salvos com sucesso!"
            )

        except OSError as error:
            messagebox.showerror("Erro", str(error))

    # ---------------- ENCERRAMENTO ----------------

    def close(self):

        self.pause()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DaviaPhysicsLab(root)
    root.mainloop()
    
