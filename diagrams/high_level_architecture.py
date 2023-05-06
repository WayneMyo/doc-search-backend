from diagrams import Diagram
from diagrams.aws.general import Users

output_dir = "diagrams/generated_diagrams/"

with Diagram("High Level Architecture", show=False, filename=output_dir + "high_level_architecture", outformat="png"):
    users = Users("External Users")

    users

"""

"""
