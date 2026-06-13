import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class QueueCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("排队剩余时间计算器")
        self.root.geometry("540x660")
        self.root.resizable(False, False)

        # 存储进度记录: [(time_obj, number), ...]
        self.records = []

        self.setup_ui()

    def _make_hour_list(self):
        return [f"{h:02d}" for h in range(24)]

    def _make_minute_list(self):
        return [f"{m:02d}" for m in range(60)]

    def _get_time_from_combos(self, hour_combo, min_combo):
        h = hour_combo.get().strip()
        m = min_combo.get().strip()
        if h and m:
            return f"{h}:{m}"
        return ""

    def _set_now_to_combos(self, hour_combo, min_combo):
        now = datetime.now()
        hour_combo.set(f"{now.hour:02d}")
        min_combo.set(f"{now.minute:02d}")

    def setup_ui(self):
        hour_list = self._make_hour_list()
        min_list = self._make_minute_list()
        now = datetime.now()

        # ========== 取号信息 ==========
        frame_info = ttk.LabelFrame(self.root, text="取号信息", padding=10)
        frame_info.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(frame_info, text="取号时间:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        time_frame = ttk.Frame(frame_info)
        time_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.combo_ticket_hour = ttk.Combobox(time_frame, values=hour_list, width=4, state="readonly")
        self.combo_ticket_hour.pack(side="left")
        self.combo_ticket_hour.set("08")
        ttk.Label(time_frame, text=":").pack(side="left", padx=1)
        self.combo_ticket_min = ttk.Combobox(time_frame, values=min_list, width=4, state="readonly")
        self.combo_ticket_min.pack(side="left")
        self.combo_ticket_min.set("00")

        ttk.Label(frame_info, text="取号号码:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_ticket_number = ttk.Entry(frame_info, width=15)
        self.entry_ticket_number.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.entry_ticket_number.insert(0, "A100")

        # ========== 当前进度输入 ==========
        frame_progress = ttk.LabelFrame(self.root, text="输入当前进度", padding=10)
        frame_progress.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_progress, text="当前时间:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        time_frame2 = ttk.Frame(frame_progress)
        time_frame2.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.combo_cur_hour = ttk.Combobox(time_frame2, values=hour_list, width=4, state="readonly")
        self.combo_cur_hour.pack(side="left")
        self.combo_cur_hour.set(f"{now.hour:02d}")
        ttk.Label(time_frame2, text=":").pack(side="left", padx=1)
        self.combo_cur_min = ttk.Combobox(time_frame2, values=min_list, width=4, state="readonly")
        self.combo_cur_min.pack(side="left")
        self.combo_cur_min.set(f"{now.minute:02d}")

        ttk.Label(frame_progress, text="当前叫到号码:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_current_number = ttk.Entry(frame_progress, width=15)
        self.entry_current_number.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(frame_progress)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="添 加 记 录", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="清 空 记 录", command=self.clear_records).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="当前时间", command=self.fill_current_time).pack(side="left", padx=5)

        # ========== 进度记录列表 ==========
        frame_list = ttk.LabelFrame(self.root, text="进度记录", padding=10)
        frame_list.pack(fill="both", expand=True, padx=10, pady=5)

        self.listbox = tk.Listbox(frame_list, height=5, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ========== 计算结果 ==========
        frame_result = ttk.LabelFrame(self.root, text="计算结果", padding=10)
        frame_result.pack(fill="x", padx=10, pady=5)

        self.result_text = tk.Text(frame_result, height=9, font=("Microsoft YaHei", 10), state="disabled", wrap="word")
        self.result_text.pack(fill="x")

        # ========== 底部按钮 ==========
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(bottom_frame, text="计算预计到达时间", command=self.calculate).pack(side="left", padx=5)

    def fill_current_time(self):
        """用当前系统时间填充当前时间下拉框"""
        now = datetime.now()
        self.combo_cur_hour.set(f"{now.hour:02d}")
        self.combo_cur_min.set(f"{now.minute:02d}")

    def parse_time(self, time_str: str) -> datetime | None:
        """解析时间字符串为 datetime 对象（以今天为基准）"""
        time_str = time_str.strip()
        try:
            parsed = datetime.strptime(time_str, "%H:%M")
            return parsed.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        except ValueError:
            return None

    def parse_number(self, number_str: str) -> int | None:
        """解析号码字符串，提取数字部分用于比较"""
        number_str = number_str.strip()
        if not number_str:
            return None
        import re
        nums = re.findall(r'\d+', number_str)
        if nums:
            return int(nums[-1])
        return None

    def add_record(self):
        current_time_str = self._get_time_from_combos(self.combo_cur_hour, self.combo_cur_min)
        current_number_str = self.entry_current_number.get().strip()

        if not current_time_str or not current_number_str:
            messagebox.showwarning("提示", "请选择当前时间并填写当前叫到号码")
            return

        time_obj = self.parse_time(current_time_str)
        if time_obj is None:
            messagebox.showwarning("提示", "时间格式错误")
            return

        number_val = self.parse_number(current_number_str)
        if number_val is None:
            messagebox.showwarning("提示", "号码格式错误，请包含数字（如 A101 或 101）")
            return

        self.records.append((time_obj, number_val, current_number_str))
        display_str = f"{current_time_str}  →  {current_number_str} (序号 {number_val})"
        self.listbox.insert(tk.END, display_str)
        self.listbox.see(tk.END)

        # 清空号码输入
        self.entry_current_number.delete(0, tk.END)

        # 自动计算
        ticket_time_str = self._get_time_from_combos(self.combo_ticket_hour, self.combo_ticket_min)
        ticket_num = self.entry_ticket_number.get().strip()
        if ticket_time_str and ticket_num:
            self.calculate()

    def clear_records(self):
        self.records.clear()
        self.listbox.delete(0, tk.END)
        self.update_result("记录已清空。")

    def calculate(self):
        ticket_time_str = self._get_time_from_combos(self.combo_ticket_hour, self.combo_ticket_min)
        ticket_number_str = self.entry_ticket_number.get().strip()

        if not ticket_time_str or not ticket_number_str:
            messagebox.showwarning("提示", "请先填写取号时间和取号号码")
            return

        ticket_time = self.parse_time(ticket_time_str)
        if ticket_time is None:
            messagebox.showwarning("提示", "取号时间格式错误")
            return

        my_number = self.parse_number(ticket_number_str)
        if my_number is None:
            messagebox.showwarning("提示", "取号号码格式错误")
            return

        if len(self.records) < 1:
            self.update_result(f"📋 你的取号信息:\n"
                               f"   号码: {ticket_number_str}  |  取号时间: {ticket_time.strftime('%H:%M')}\n\n"
                               f"请至少输入一条当前进度记录以估算剩余时间。")
            return

        # 排序记录（按时间）
        sorted_records = sorted(self.records, key=lambda x: x[0])

        # 取最后一条记录
        latest_time, latest_number, latest_number_str = sorted_records[-1]

        # 计算已过去的分钟数
        minutes_since_ticket = (latest_time - ticket_time).total_seconds() / 60.0

        # 计算叫号数量
        ticket_num_val = self.parse_number(ticket_number_str)
        numbers_served = latest_number - ticket_num_val

        # 计算速度
        if minutes_since_ticket > 0 and numbers_served > 0:
            speed = numbers_served / minutes_since_ticket
        else:
            if len(sorted_records) >= 2:
                r1 = sorted_records[-2]
                r2 = sorted_records[-1]
                time_diff = (r2[0] - r1[0]).total_seconds() / 60.0
                num_diff = r2[1] - r1[1]
                if time_diff > 0 and num_diff > 0:
                    speed = num_diff / time_diff
                else:
                    speed = 0
            else:
                speed = 0

        # 剩余号码数
        remaining_numbers = my_number - latest_number

        # 计算剩余时间
        remaining_time_min = 0
        if speed > 0 and remaining_numbers > 0:
            remaining_time_min = remaining_numbers / speed
        elif remaining_numbers <= 0:
            remaining_time_min = 0
        else:
            remaining_time_min = -1

        # 预计到达时间
        now = datetime.now()
        if remaining_time_min > 0:
            estimated_arrival = now + timedelta(minutes=remaining_time_min)
            arrival_str = estimated_arrival.strftime("%H:%M")
        elif remaining_time_min == 0:
            arrival_str = "已到达"
        else:
            arrival_str = "无法估算"

        # ===== 构建输出信息 =====
        lines = []

        # 第一段：醒目显示预计到号时间
        if remaining_numbers > 0 and speed > 0:
            lines.append(f"════════════════════════════")
            lines.append(f"   ⏰ 预计到号时间: {arrival_str}")
            lines.append(f"════════════════════════════")
            lines.append("")
            lines.append(f"📋 你的号码: {ticket_number_str}  |  取号: {ticket_time.strftime('%H:%M')}")
            lines.append(f"📊 当前进度: 第 {latest_number_str} 号 ({latest_time.strftime('%H:%M')})")
            lines.append(f"")
            lines.append(f"  已叫号: {numbers_served} 个  |  用时: {minutes_since_ticket:.0f} 分钟")
            lines.append(f"  处理速度: {speed:.2f} 个/分钟")
            lines.append(f"  你前面还有: {remaining_numbers} 个号")

            if remaining_time_min < 60:
                lines.append(f"  预计还需: {remaining_time_min:.0f} 分钟")
            else:
                h = int(remaining_time_min // 60)
                m = int(remaining_time_min % 60)
                lines.append(f"  预计还需: {h} 小时 {m} 分钟")
            lines.append(f"")

            # 近期速度参考
            if len(sorted_records) >= 2:
                r1 = sorted_records[-2]
                r2 = sorted_records[-1]
                seg_time = (r2[0] - r1[0]).total_seconds() / 60.0
                seg_num = r2[1] - r1[1]
                if seg_time > 0 and seg_num > 0:
                    seg_speed = seg_num / seg_time
                    seg_remaining = remaining_numbers / seg_speed
                    seg_arrival = r2[0] + timedelta(minutes=seg_remaining)
                    lines.append(f"─" * 32)
                    lines.append(f"💡 近期速度参考:")
                    lines.append(f"  {r1[0].strftime('%H:%M')} → {r2[0].strftime('%H:%M')}")
                    lines.append(f"  处理了 {seg_num} 个, 用时 {seg_time:.0f} 分钟")
                    lines.append(f"  速度: {seg_speed:.2f} 个/分钟")
                    if seg_remaining < 60:
                        lines.append(f"  预计还需: {seg_remaining:.0f} 分钟")
                    else:
                        h = int(seg_remaining // 60)
                        m = int(seg_remaining % 60)
                        lines.append(f"  预计还需: {h} 小时 {m} 分钟")
                    lines.append(f"  预计到达: {seg_arrival.strftime('%H:%M')}")

        elif remaining_numbers <= 0:
            lines.append(f"════════════════════════════")
            lines.append(f"      ✅ 已经叫到你的号码了！")
            lines.append(f"       快去柜台办理！")
            lines.append(f"════════════════════════════")
        else:
            lines.append(f"📋 你的号码: {ticket_number_str}  |  取号: {ticket_time.strftime('%H:%M')}")
            lines.append(f"📊 当前进度: 第 {latest_number_str} 号 ({latest_time.strftime('%H:%M')})")
            lines.append(f"")
            lines.append(f"⚠️ 数据不足，暂时无法估算速度。")
            lines.append(f"请再添加一条进度记录后重新计算。")

        self.update_result("\n".join(lines))

    def update_result(self, text: str):
        self.result_text.configure(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        self.result_text.configure(state="disabled")


def main():
    root = tk.Tk()
    app = QueueCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
