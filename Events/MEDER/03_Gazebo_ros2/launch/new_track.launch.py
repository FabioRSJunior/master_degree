#!/usr/bin/env python3
# Adapted from:
# Copyright 2019 ROBOTIS CO., LTD.
# Authors: Darby Lim

# Modificado por: Fabio Romero de Souza Junior 

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import TimerAction

TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file_name = 'new_track.world'
    world = os.path.join(get_package_share_directory('follower'), world_file_name)
    turtlebot_launch_dir = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
            ),
            launch_arguments={'world': world}.items(),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
            ),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([turtlebot_launch_dir, '/robot_state_publisher.launch.py']),
            launch_arguments={'use_sim_time': use_sim_time}.items(),
        ),

        # Adicionar novos nós aqui
        Node(
            package='follower',
            executable='follower_node',
            name='follower',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        Node( 
            package='follower', 
            executable='data_collector', 
            name='data_collector', 
            output='screen', 
            parameters=[{'use_sim_time': True}]  
        ),
        Node( 
            package='follower',
            executable='image_receiver',
            name='image_receiver_node',
            output='screen',
            parameters=[{'use_sim_time': True}]
         ),
         Node(
            package='follower',
            executable='manual_controller',
            name='manual_controller',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),
        Node(
            package='follower',
            executable='simulation_node',
            name='simulation_node',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),
    ])

