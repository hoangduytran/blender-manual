import bpy
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

GEO_NODES_PASS = [
    "GeometryNodeCustomGroup",
    "GeometryNodeGroup",
    "GeometryNodeRepeatInput",
    "GeometryNodeRepeatOutput",
    "GeometryNodeSimulationInput",
    "GeometryNodeSimulationOutput"
]

@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float


def cut_image(old_path, new_path, rect):
    image = bpy.data.images.load(old_path)

    total_width, total_height = image.size
    assert total_width >= rect.x + rect.width
    assert total_height >= rect.y + rect.height

    old_pixels = image.pixels
    new_pixels = []

    for y in range(rect.y, rect.y + rect.height):
        row_start = y * total_width + rect.x
        row_end = row_start + rect.width
        new_pixels.extend(old_pixels[4 * row_start:4 * row_end])

    image.scale(rect.width, rect.height)
    image.pixels = new_pixels
    image.filepath_raw = new_path
    image.save()

    bpy.data.images.remove(image)


def node_region_rect(region, node):
    location = node.location
    dimensions = node.dimensions

    view_to_region = region.view2d.view_to_region
    bottom_left = view_to_region(
        location.x, location.y - dimensions.y, clip=False)
    top_right = view_to_region(
        location.x + dimensions.x, location.y, clip=False)

    return Rectangle(bottom_left[0], bottom_left[1], top_right[0] - bottom_left[0], top_right[1] - bottom_left[1])


def iter_node_names(tree_type):
    if tree_type == 'GEOMETRY':
        for cls in bpy.types.GeometryNode.__subclasses__():
            if cls.__name__ in GEO_NODES_PASS:
                continue
            yield cls.__name__
        for cls in bpy.types.FunctionNode.__subclasses__():
            yield cls.__name__
    elif tree_type == 'COMPOSITING':
        for cls in bpy.types.CompositorNode.__subclasses__():
            yield cls.__name__
    elif tree_type == 'SHADER':
        for cls in bpy.types.ShaderNode.__subclasses__():
            yield cls.__name__
    elif tree_type == 'TEXTURE':
        for cls in bpy.types.TextureNode.__subclasses__():
            yield cls.__name__


class MakeScreenshotsOperator(bpy.types.Operator):
    bl_idname = "test.make_screenshots"
    bl_label = "Make Screenshots"

    only_selected: bpy.props.BoolProperty(
        name="Only Selected Nodes",
        description="Only create screenshots for selected nodes",
        default=False
    )

    def invoke(self, context, event):
        # Prompt user for confirmation
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # Start the modal operation after confirmation
        context.window_manager.modal_handler_add(self)

        node_tree = context.space_data.node_tree
        if self.only_selected:
            selected_nodes = [node for node in node_tree.nodes if node.select]
            if not selected_nodes:
                self.report({'WARNING'}, "No nodes selected!")
                return {'CANCELLED'}
            self.selected_nodes = selected_nodes
            self.selected_index = 0
            return self.prepare_selected_node(context)
        else:
            tree_type = node_tree.type
            self.node_names_iterator = islice(iter_node_names(tree_type), 10000)
            return self.prepare_next_node(context)

    def prepare_selected_node(self, context):
        if self.selected_index >= len(self.selected_nodes):
            return {'FINISHED'}

        # Get the current node and deselect it
        self.current_node = self.selected_nodes[self.selected_index]
        self.current_name = self.current_node.bl_idname
        self.selected_nodes[self.selected_index].select = False  # Deselect the node

        self.selected_index += 1
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def prepare_next_node(self, context):
        try:
            node_name = next(self.node_names_iterator)
        except:
            return {'FINISHED'}

        node_tree = context.space_data.node_tree
        for node in node_tree.nodes:
            node.location.x = 10000
        node = node_tree.nodes.new(node_name)
        node.select = False
        node.show_preview = False
        self.current_node = node
        self.current_name = node_name
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        base_path = Path.home() / "Downloads" / "node_screenshots"
        temp_path = str(base_path / "temp.png")
        filepath = str(base_path / f"node-types_{self.current_name}.png")
        bpy.ops.screen.screenshot_area(filepath=temp_path)

        rect = node_region_rect(context.region, self.current_node)
        margin = 15
        rect.x -= margin
        rect.y -= margin
        rect.width += margin * 2
        rect.height += margin * 2

        cut_image(temp_path, filepath, rect)
        context.area.tag_redraw()

        if self.only_selected:
            return self.prepare_selected_node(context)
        return self.prepare_next_node(context)


bpy.utils.register_class(MakeScreenshotsOperator)
