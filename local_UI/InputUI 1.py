import tkinter as tk
from tkinter import font, ttk, messagebox
import joblib
import random
import os

# Color scheme
DARK_BLUE = "#1a365d"
MEDIUM_BLUE = "#2c5282"
LIGHT_BLUE = "#ebf8ff"
WHITE = "#ffffff"
GREEN = "#48bb78"
RED = "#f56565"
BUTTON_COLOR = "#4299e1"
BUTTON_HOVER = "#3182ce"

# Dictionary to store our models
MODELS = {
    'Naive Bayes': {
        'model_path': 'naive_bayes_model.pkl',
        'vectorizer_path': 'naive_bayes_vectorizer.pkl',
        'model': joblib.load("naive_bayes_model.pkl"),
        'vectorizer': joblib.load("naive_bayes_vectorizer.pkl"),
        'description': 'Fast and efficient for text classification'
    },
    'KNN': {
        'model_path': 'knn_model.pkl',
        'vectorizer_path': 'knn_vectorizer.pkl',
        'model': joblib.load("knn_model.pkl"),
        'vectorizer': joblib.load("knn_vectorizer.pkl"),
        'description': 'Instance-based learning for classification'
    },
    'Random Forest': {
        'model_path': 'random_forest_model.pkl',
        'vectorizer_path': 'random_forest_vectorizer.pkl',
        'model': None,
        'vectorizer': None,
        'description': 'Ensemble learning method using multiple decision trees'
    }
}

class PhishingDetectorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Model Phishing Email Detection")
        self.setup_window()
        self.create_styles()
        self.create_ui_elements()
        self.bind_events()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        
        # Create main frame with fixed height for results
        self.root_frame = tk.Frame(self.root)
        self.root_frame.pack(fill="both", expand=True)
        self.root_frame.grid_rowconfigure(0, weight=1)
        self.root_frame.grid_columnconfigure(0, weight=1)
        
        # Background canvas with gradient
        self.canvas = tk.Canvas(self.root_frame, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
    def create_styles(self):
        """Create custom styles and fonts"""
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.content_font = font.Font(family="Helvetica", size=12)
        self.result_font = font.Font(family="Helvetica", size=16, weight="bold")
        
    def create_gradient(self):
        """Create gradient background"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        for i in range(height):
            ratio = i / height
            r1, g1, b1 = self.canvas.winfo_rgb(DARK_BLUE)
            r2, g2, b2 = self.canvas.winfo_rgb(MEDIUM_BLUE)
            r = int(r1 + (r2 - r1) * ratio) // 256
            g = int(g1 + (g2 - g1) * ratio) // 256
            b = int(b1 + (b2 - b1) * ratio) // 256
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, width, i, fill=color)
            
    def create_ui_elements(self):
        """Create all UI elements"""
        # Title with enhanced styling
        self.title_label = tk.Label(
            self.root,
            text="Multi-Model Phishing Email Detection",
            font=self.title_font,
            fg=WHITE,
            bg=MEDIUM_BLUE,
            padx=20,
            pady=10,
            relief="solid"
        )
        
        # Instruction label
        self.instruction_label = tk.Label(
            self.root,
            text="Select models and enter email content for analysis",
            font=self.label_font,
            fg=WHITE,
            bg=MEDIUM_BLUE,
            justify="center",
            padx=15,
            pady=5
        )
        
        # Main container
        self.main_container = tk.Frame(self.root, bg=LIGHT_BLUE)
        
        # Model selection frame
        self.create_model_selection_frame()
        
        # Input frame
        self.create_input_frame()
        
        # Results frame
        self.create_results_frame()
        
        # Update layout
        self.update_layout()
        
    def create_model_selection_frame(self):
        """Create model selection section"""
        model_frame = tk.LabelFrame(
            self.main_container,
            text="Select Models for Analysis",
            font=self.label_font,
            bg=LIGHT_BLUE,
            fg=DARK_BLUE,
            pady=10
        )
        model_frame.pack(fill="x", padx=20, pady=10)
        
        # Model checkboxes
        self.model_vars = {}
        for i, (model_name, info) in enumerate(MODELS.items()):
            var = tk.BooleanVar(value=True)
            self.model_vars[model_name] = var
            
            checkbox = tk.Checkbutton(
                model_frame,
                text=model_name,
                variable=var,
                font=self.content_font,
                bg=LIGHT_BLUE,
                fg=DARK_BLUE
            )
            checkbox.grid(row=0, column=i, padx=10, pady=5)
            
    def create_input_frame(self):
        """Create input section"""
        input_frame = tk.LabelFrame(
            self.main_container,
            text="Email Content",
            font=self.label_font,
            bg=LIGHT_BLUE,
            fg=DARK_BLUE,
            pady=10
        )
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Scrollable input area
        input_scroll = tk.Scrollbar(input_frame)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.input_field = tk.Text(
            input_frame,
            font=self.content_font,
            height=6,
            wrap=tk.WORD,
            yscrollcommand=input_scroll.set,
            padx=10,
            pady=10,
            bg=WHITE,
            fg=DARK_BLUE,
            relief="solid",
            borderwidth=1
        )
        self.input_field.pack(fill="both", expand=True, padx=10)
        input_scroll.config(command=self.input_field.yview)
        
        # Analyze button
        self.submit_button = tk.Button(
            self.main_container,
            text="Analyze Email",
            command=self.analyze_email,
            font=self.label_font,
            bg=BUTTON_COLOR,
            fg=WHITE,
            activebackground=BUTTON_HOVER,
            activeforeground=WHITE,
            relief="solid",
            borderwidth=1,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        self.submit_button.pack(pady=10)
        
    def create_results_frame(self):
        """Create results section with scrollable canvas"""
        # Create outer frame
        results_container = tk.Frame(self.main_container, bg=LIGHT_BLUE)
        results_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(results_container, bg=LIGHT_BLUE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=canvas.yview)
        
        # Create frame for results inside canvas
        self.results_frame = tk.Frame(canvas, bg=LIGHT_BLUE)
        
        # Configure canvas
        self.results_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window inside canvas
        canvas_frame = canvas.create_window((0, 0), window=self.results_frame, anchor="nw", width=canvas.winfo_reqwidth())
        
        # Configure canvas scroll
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas resize to frame resize
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def update_layout(self, event=None):
        """Update layout when window size changes"""
        # Clear existing canvas items
        self.canvas.delete("all")
        
        # Redraw gradient
        self.create_gradient()
        
        # Get current window dimensions
        width = self.canvas.winfo_width()
        
        # Update positions of all elements
        self.title_label.place(relx=0.5, rely=0.05, anchor="center")
        self.instruction_label.place(relx=0.5, rely=0.12, anchor="center")
        
        # Update container frame position and size
        container_width = min(int(width * 0.8), 1000)
        self.main_container.place(relx=0.5, rely=0.2, anchor="n", width=container_width)
        
    def bind_events(self):
        """Bind window events"""
        self.root.bind('<Configure>', self.update_layout)
        self.root.bind('<Return>', lambda event: self.analyze_email())
        self.root.bind("<F11>", lambda event: self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen')))
        self.root.bind("<Escape>", lambda event: self.root.attributes('-fullscreen', False))
        
    def analyze_email(self):
        """Handle email analysis"""
        email_content = self.input_field.get("1.0", tk.END).strip()
        if not email_content:
            messagebox.showwarning("Input Required", "Please enter email content for analysis.")
            return
            
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Process with each selected model
        selected_models = [name for name, var in self.model_vars.items() if var.get()]
        
        if not selected_models:
            messagebox.showwarning("Model Selection Required", "Please select at least one model for analysis.")
            return
            
        for model_name in selected_models:
            self.process_with_model(email_content, model_name)
            
    def process_input(self, input_text, model_name):
        """
        Process input text using specified model.
        
        Args:
            input_text (str): The email content to analyze
            model_name (str): Name of the model to use
            
        Returns:
            dict: Contains classification results and confidence scores
        """
        try:
            model_info = MODELS[model_name]
            model = model_info['model']
            vectorizer = model_info['vectorizer']
            
            if model is None or vectorizer is None:
                return {
                    'classification': 'Error',
                    'confidence': 0.0,
                    'error': 'Model not loaded'
                }
            
            # Transform input text using model's vectorizer
            input_vectorized = vectorizer.transform([input_text])
            
            # Get prediction probabilities
            probabilities = model.predict_proba(input_vectorized)[0]
            
            # Get predicted class using argmax
            predicted_class = model.classes_[probabilities.argmax()]
            
            # Calculate confidence as highest probability
            confidence = probabilities.max() * 100
            
            # Determine classification
            classification = 'Phishing' if predicted_class == 'Phishing Email' else 'Safe Email'
            
            return {
                'classification': classification,
                'confidence': confidence,
                'error': None
            }
            
        except Exception as e:
            return {
                'classification': 'Error',
                'confidence': 0.0,
                'error': str(e)
            }
            
    def process_with_model(self, content, model_name):
        """Process input with a specific model and display results"""
        try:
            # Process the input
            result = self.process_input(content, model_name)
            
            if result['error']:
                raise Exception(result['error'])
                
            self.display_result(model_name, result['classification'], result['confidence'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing with {model_name}: {str(e)}")
            
    def display_result(self, model_name, classification, confidence):
        """Display analysis result for a specific model"""
        result_section = tk.LabelFrame(
            self.results_frame,
            text=f"Results from {model_name}",
            font=self.label_font,
            bg=LIGHT_BLUE,
            fg=DARK_BLUE
        )
        result_section.pack(fill="x", padx=20, pady=5, expand=False)  # Prevent expansion
        
        result_frame = tk.Frame(result_section, bg=LIGHT_BLUE)
        result_frame.pack(fill="x", padx=15, pady=10)
        
        # Status indicator
        is_safe = "Safe" in classification
        status_color = GREEN if is_safe else RED
        status_text = "✓ SAFE EMAIL" if is_safe else "⚠ PHISHING DETECTED"
        
        status_label = tk.Label(
            result_frame,
            text=status_text,
            font=self.result_font,
            bg=status_color,
            fg=WHITE,
            padx=20,
            pady=10,
            relief="solid"
        )
        status_label.pack(pady=(5,0))
        
        # Confidence level
        confidence_label = tk.Label(
            result_frame,
            text=f"Confidence Level: {confidence:.2f}%",
            font=self.content_font,
            bg=LIGHT_BLUE,
            fg=DARK_BLUE
        )
        confidence_label.pack(pady=5)
        
def main():
    root = tk.Tk()
    app = PhishingDetectorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()