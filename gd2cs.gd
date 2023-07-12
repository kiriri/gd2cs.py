@tool
extends EditorPlugin

var popup:Window
var enabled := false;

func get_files_container():
	return popup.get_node("VBoxContainer/TopBottomSplit/LeftRightSplit/Panel_L/Files/Files");
	
func get_regex_container(): 
	return  popup.get_node("VBoxContainer/TopBottomSplit/LeftRightSplit/Panel_R/NameRepl/NameReplace");

func get_console():
	return popup.get_node("VBoxContainer/TopBottomSplit/Console/ScrollContainer/VBoxContainer")

func print_to_console(text:String,color:Color = Color.WHITE)->Label:
	var line = Label.new()
	line.text = text;  
	line.self_modulate = color;
	get_console().add_child(line)
	
	return line

# TODO : Find FileSystem's context meny by searching for its default elements
#func search(node:Node):
#	if ('text' in node and 'to Favorites' in node.text or 
#	'label' in node and 'to Favorites' in node.label) and not 'TextEdit' in str(node.get_path()):
#		print(node.get_path())
#
#
#	for child in node.get_children():
#		search(child)
#

	
# Process the actual conversion
func do_conversion():
	var files = get_files()
	var executable = popup.find_child('PythonExecutable').text
	var rename_vars = popup.find_child("RenameVariables").pressed;
	var rename_funcs = popup.find_child("RenameFunctions").pressed;
	var remove_res = RegEx.new()
	remove_res.compile("^res://")
	for file in files:
		if ProjectSettings.globalize_path(file[0]) == ProjectSettings.globalize_path(file[1]):
			print_to_console("Error: Input file path is equivalent to output file path. " + file[0] + " . SKIPPED!",Color.RED)
			continue 
		
		file[0] = remove_res.sub(file[0],"")
		file[1] = remove_res.sub(file[1],"")
		var params = ["addons/gd2cs.py/gd2cs.py","-i",file[0],"-o",file[1]]
		if rename_funcs:
			params.append("--rename_functions")
		if rename_vars:
			params.append("--rename_variables")
		params.append("--is_not_console") # So any input action leads to quit
		run_os_code(executable, params)
		get_editor_interface().get_resource_filesystem().update_file(file[1]) 

# Run OS/shell code. Print results and errors to console
func run_os_code(executable:String,params:Array):
	var output = [];
	var return_code = OS.execute(executable,params,output,true,true)
	if return_code != 0 : 
		print_to_console("ERROR : Python exited with code " + str(return_code), Color.RED)
	for out in output:
		if "This Script requires the regex package." in out:
			popup.find_child("NoRegexDialog").popup_centered()
		print_to_console(out+"\n")
	return output

# Read the files from the files list as an array of [input_path,output_path,node in list]
func get_files()->Array:
	var result = []
	var input_list = get_files_container()
	for node in input_list.get_children():
		var input = node.find_child("Input").text;
		var output = node.find_child("Output").text;
		result.append([input,output,node])
	return result;

# Create the matching ui elements once the files were submitted
func add_input(paths):
	var inputs_list = get_files_container()
	for child in paths:
		var child_node : Node = load("res://addons/gd2cs.py/scenes/FileElement.tscn").instantiate()
		child_node.find_child("Input").text = child
		child_node.find_child("Output").text = input_to_output(child)
		inputs_list.add_child(child_node);

# Turn input name to output name
func input_to_output(input:String)->String:
	var name_replace = get_regex_container()
	for child in name_replace.get_children():
		var r = RegEx.new()
		r.compile(child.find_child("ReplaceMatch").text);
		input = r.sub(input,child.find_child("ReplaceSub").text,true);
	return input

# Prompt the user to select input files
func select_input():
	var file_dialogue = popup.find_child("EditorFileDialog");
	file_dialogue.popup_centered()

# Add a new rename rule
func add_rename_rule():
	var rename_list = get_regex_container();
	var child_node : Node = load("res://addons/gd2cs.py/scenes/ReplaceElement.tscn").instance();
	rename_list.add_child(child_node); 

# Set all output paths to their corresponding input paths
# The python will automatically add a .cs if none exists at the end of the name,
# So overwriting the source gd file should be impossible
func reset_outputs(): 
	var files = get_files()
	for file in files:
		var node = file[2];
		node.find_child("Output").text = file[0] 

# Apply the regex rename to all output file paths
func rename_all():
	var files = get_files()
	for file in files:
		var node = file[2];
		node.find_child("Output").text = input_to_output(file[1])


# Check all common path aliases for the python executable. Prefer python3 over python2.
func get_best_python_exec():
	if ProjectSettings.has_setting("gd2cs/config/python"):
		var exec = ProjectSettings.get_setting("gd2cs/config/python")
		if not exec in ["null",""]:
			return exec;
	
	var output = [];
	var options = ["py","python3","python","python2"];
	for option in options:
		if OS.execute(option,["--version"],output,true) == 0:
			ProjectSettings.set_setting("gd2cs/config/python",option)
			return option
	
	print_to_console("No valid python install could be detected.",Color.RED)
	
	if ProjectSettings.get_setting("gd2cs/config/ask_no_python"):
		popup.find_child("NoPythonDialog").popup_centered(Vector2(400,400));
	
	return "#NO PYTHON FOUND#" # No installed python env found

func change_python_exec(val):
	ProjectSettings.set_setting("gd2cs/config/python",val)

func set_ask_no_python(val):
	ProjectSettings.set_setting("gd2cs/config/ask_no_python",not val)

# Download python. For now, open a download url. Still debating on whether
# an auto-install would be appreciated here...
func download_python():
	OS.shell_open("https://www.python.org/downloads/")
	popup.find_child("NoPythonDialog").hide()	
	popup.hide()

# Install the regex python module. This happens automatically in the background via pip.
func install_regex():
	run_os_code(ProjectSettings.get_setting("gd2cs/config/python"),["-m","pip","install","regex"])
	popup.find_child("NoRegexDialog").hide()
	do_conversion()
	
func hide_popup():
	popup.hide()

# Called if the Project->Tools->gd2cs button is clicked. Opens the popup.
func callback():  
	if not popup : 
		popup = load("res://addons/gd2cs.py/scenes/Editor_UI.tscn").instantiate();
		add_child(popup)
		popup.connect("close_requested", hide_popup)
		popup.find_child("EditorFileDialog").add_filter("*.gd") 
		popup.find_child("EditorFileDialog").connect("files_selected", add_input) 
		popup.find_child("SelectInput").connect("pressed",select_input)
		popup.find_child("AddRR").connect("pressed",add_rename_rule)
		popup.find_child('PythonExecutable').connect("text_changed",change_python_exec)
		popup.find_child("ConvertButton").connect("button_up",do_conversion)		
		popup.find_child("ResetNames").connect("pressed",reset_outputs)		
		popup.find_child("ApplyRename").connect("pressed",rename_all)		
		popup.find_child("DontAskAgain").connect("toggled",set_ask_no_python)		
		popup.find_child("DownloadPython").connect("pressed",download_python)
		popup.find_child("NoRegexDialog").find_child("InstallRegex").connect("pressed",install_regex)
		print_to_console("Console Initialized") 
	
	popup.find_child('PythonExecutable').text = get_best_python_exec()
	popup.popup_centered(Vector2(800,600));

func _enter_tree():
	enabled = true;
	if not ProjectSettings.has_setting("gd2cs/config/ask_no_python"):
		ProjectSettings.set_setting("gd2cs/config/ask_no_python",true)
	add_tool_menu_item("gd2cs", callback)
	
func _exit_tree():
	enabled = false;
	remove_tool_menu_item("gd2cs")
