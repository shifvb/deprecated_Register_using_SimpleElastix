# page control frame
self.page_ctrl_frame = tk.Frame(right_frame, width=384, height=30)
self.page_ctrl_frame.propagate(False)
self.page_ctrl_frame.grid(row=1, column=0, sticky=tk.NS)
self.prev_btn = tk.Button(self.page_ctrl_frame, text="prev image", font=Font(size=15),
                          command=prev_image_callback)

self.next_btn = tk.Button(self.page_ctrl_frame, text="next image", font=Font(size=15),
                          command=next_image_callback)

self.next_btn.pack(side=tk.RIGHT)
self.prev_btn.pack(side=tk.RIGHT)
