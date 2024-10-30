import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class ModifiedRegexGUI:
    def __init__(self, root):
        self.string = ModifiedRegex()
        
        root.title("ModifiedRegex Interface")
        root.geometry("500x300")
        root.configure(bg="#f2f2f2")

        self.title_label = tk.Label(root, text="ModifiedRegex Interface", font=("Arial", 16), bg="#f2f2f2")
        self.title_label.pack(pady=10)

        self.label = tk.Label(root, text="Ingrese el patrón de búsqueda:", bg="#f2f2f2", fg="black")
        self.label.pack(pady=5)

        self.pattern_entry = tk.Entry(root, width=50)
        self.pattern_entry.pack(pady=5)

        self.file_button = tk.Button(root, text="Seleccionar Archivo", command=self.load_file, bg="#1e90ff", fg="white")
        self.file_button.pack(pady=10)

        self.credits_button = tk.Button(root, text="Créditos", command=self.show_credits, bg="#1e90ff", fg="white")
        self.credits_button.pack(pady=5)

        self.search_button = tk.Button(root, text="Buscar", command=self.search_pattern, bg="#1e90ff", fg="white")
        self.search_button.pack(pady=10)

        self.result_text = scrolledtext.ScrolledText(root, width=40, height=5, wrap=tk.WORD)
        self.result_text.pack(pady=10)
        self.result_text.config(state=tk.DISABLED)

    def load_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.string.set_text(file_path)
            messagebox.showinfo("Información", "Archivo subido correctamente!")

    def search_pattern(self):
        pattern = self.pattern_entry.get()
        result = self.string.query(pattern)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        if result:
            self.result_text.insert(tk.END, f"Se encontró el patrón en las posiciones: {result}")
        else:
            self.result_text.insert(tk.END, ":(")
        self.result_text.config(state=tk.DISABLED)

    def show_credits(self):
        messagebox.showinfo("Créditos", "Autores:\n\nValeria y Zeus")





class ModifiedRegex():
    def __init__(self):
        self.text = ""
        self.ALPHABET_SIZE = 130
        self.bmt = {}
        self.filename = ""
        self.i = False
        self.g = False

    def set_text(self, filename):
        self.filename = filename
        with open(filename, 'r') as a:
            self.text = a.read()

    def __char_to_index(self, char):
        return ord(char)

    def __calculate_bad_match_table(self, pattern):
        l = len(pattern)
        # Crear la tabla
        self.bmt = [1] * self.ALPHABET_SIZE
        for i in range(l - 1):
            s = self.__char_to_index(pattern[i])
            self.bmt[s - 1] = l - i -1 

        return self.bmt
    
    def busqueda_simple_from(self, pattern, start_idx):
        text = self.text
        if self.i:
            pattern = pattern.lower()
            text = self.text.lower()

        matches = []
        bad_match_table = self.__calculate_bad_match_table(pattern)  
        patt_size = len(pattern)
        text_idx = start_idx + patt_size - 1

        while text_idx < len(text):
            shared_substr = 0
            while shared_substr < patt_size:
                if text[text_idx - shared_substr] == pattern[patt_size - shared_substr - 1]:
                    shared_substr += 1
                else:
                    break  

            if shared_substr == patt_size:
                matches.append(text_idx - patt_size + 1)
                text_idx += 1  
            else:
                text_idx += bad_match_table[self.__char_to_index(text[text_idx]) - 1]

        return matches

    def busqueda_simple(self, pattern):
        text = self.text
        if self.i:
            pattern = pattern.lower()
            text = self.text.lower()

        matches = []
        bad_match_table = self.__calculate_bad_match_table(pattern)  
        patt_size = len(pattern)

        text_idx = patt_size - 1

        while text_idx < len(text):
            shared_substr = 0
            while shared_substr < patt_size:
                if text[text_idx - shared_substr] == pattern[patt_size - shared_substr - 1]:
                    shared_substr += 1
                else:
                    break  

            if shared_substr == patt_size:
                matches.append(text_idx - patt_size + 1)
            
            text_idx += bad_match_table[self.__char_to_index(text[text_idx]) - 1]
            
        return matches
    
    def rango_corchetes(self, pattern):
        start_idx, end_idx = -1, -1

        for i, char in enumerate(pattern):
            if char == '[' and start_idx == -1:
                start_idx = i
            elif char == ']' and end_idx == -1:
                end_idx = i

        if start_idx == -1 or end_idx == -1:
            return []

        prefix = pattern[:start_idx]
        postfix = pattern[end_idx+1:]
        middle = pattern[start_idx+1:end_idx]
        
        start_char, end_char = middle.split('-')
        matches = []

        for char in range(ord(start_char), ord(end_char)+1):
            actual_pattern = prefix + chr(char) + postfix
            matches.extend(self.busqueda_simple(actual_pattern))

        matches.sort()
        return matches
    
    def conjunto_corchetes(self, pattern):
        matches = []

        prefix = pattern.split('[')[0]
        chars_in_brackets = pattern.split('[')[1].split(']')[0]
        postfix = pattern.split(']')[1]

        for char in chars_in_brackets:
            segment = prefix + char + postfix
            matches.extend(self.busqueda_simple(segment)) 
        
        matches.sort()


        return matches

    def comodin(self, pattern):
        segments = pattern.split('*')  
        matches = []
        potential_starts = [0]

        for segment in segments:
            new_starts = []
            if segment:  # Si el segmento no está vacío
                for start in potential_starts:
                    segment_matches = self.busqueda_simple_from(segment, start)
                    new_starts.extend([match + len(segment) for match in segment_matches])
            else:  # Si el segmento está vacío (cuando hay un '' al inicio o entre dos '')
                new_starts = [start + 1 for start in potential_starts]
            
            potential_starts = new_starts

        for start in potential_starts:
            if start - len(pattern) >= 0:  
                matches.append(start - len(pattern))

        matches = list(set(matches))
        
        matches.sort()

        return matches
        
    def letra_inmediata(self, pattern):
        matches = []
        i = 0
        while i < len(pattern):
            char = pattern[i]
            if char == '?':
                if i == 0:
                    return None
                
                patron_sin = pattern[:i-1] + pattern[i + 1:]
                patron_con = pattern[:i] + pattern[i + 1:]
                break
            i += 1

        tabla1 = self.busqueda_simple(patron_sin)
        tabla2 = self.busqueda_simple(patron_con)
        
        matches = tabla1 + tabla2

        matches = list(set(matches))

        matches.sort()
        return matches
    
    def operador_or(self, pattern):
        i = 0
        pattern1 = ""
        pattern2 = ""
        while i < len(pattern):
            char = pattern[i]
            if char == '|':
                if i == 0:
                    return None
                pattern1 = pattern[:i] 
                pattern2 = pattern[i + 1:]
                break  
            i += 1
        
        if not pattern1 or not pattern2: 
            return []
        
        tabla1 = self.busqueda_simple(pattern1)
        tabla2 = self.busqueda_simple(pattern2)
        
        matches = tabla1 + tabla2
        matches = list(set(matches))
        matches.sort()
        return matches
    
    def llaves(self, pattern):
        new_pattern = ""
        i = 0
        while i < len(pattern):
            char = pattern[i]
            
            if char == '{':
                if i == 0:
                    return None
                
                cuentas = int(pattern[i + 1]) - 1
                
                new_pattern += pattern[i-1] * cuentas
                
                i += 3
                
            else:
                new_pattern += char
                i += 1

        return self.busqueda_simple(new_pattern)
    
    def interpretar_patron(self, patron):
        if "[" in patron:
            if "-" in patron:
                matches = self.rango_corchetes(patron)
            else:
                matches = self.conjunto_corchetes(patron)
        elif '*' in patron:
            matches = self.comodin(patron)
        elif '?'  in patron:
            matches = self.letra_inmediata(patron)  
        elif '|' in patron:
            matches =  self.operador_or(patron)
        elif '{' in patron:
            matches = self.llaves(patron)
        else:
            matches = self.busqueda_simple(patron)

        if not self.g and matches:
            return [matches[0]]
        
        return matches
    

    def query(self, query):
        query_completa = query.split()
 
        self.g = False
        self.i = False

        if query_completa[0] == 'f':
            if len(query_completa) > 2:
                if 'i' in query_completa[2]:
                    self.i = True
                if 'g' in query_completa[2]:
                    self.g = True
            return self.interpretar_patron(query_completa[1])
        else:
                return None






root = tk.Tk()
gui = ModifiedRegexGUI(root)
root.mainloop()