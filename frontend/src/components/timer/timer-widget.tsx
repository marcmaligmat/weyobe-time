'use client';

import { useState } from 'react';
import { useTimerStore } from '@/lib/stores/timer';
import { ValidationModal } from './validation-modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { formatTime } from '@/lib/utils';
import { Play, Square, Plus, FolderOpen, Tag } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { mockProjectsForTimer, getProjectById } from '@/lib/data/projects';

interface TimerWidgetProps {
  className?: string;
}

interface Project {
  id: string;
  name: string;
  color: string;
  client?: string;
}

export function TimerWidget({ className }: TimerWidgetProps) {
  const {
    isActive,
    elapsedTime,
    currentProject,
    description,
    startTimer,
    stopTimer,
    setCurrentProject,
    setDescription,
  } = useTimerStore();

  const [selectedProject, setSelectedProject] = useState<string>('');
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showValidationModal, setShowValidationModal] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectColor, setNewProjectColor] = useState('#03a9f4');

  const handleStartStop = async () => {
    if (isActive) {
      const result = await stopTimer();
      if (!result.success && result.errors) {
        setValidationErrors(result.errors);
        setShowValidationModal(true);
      }
    } else {
      startTimer(selectedProject || undefined);
    }
  };

  const handleCreateProject = () => {
    // In real app, this would call your API/store to create a new project
    console.log('Creating project:', { name: newProjectName, color: newProjectColor });
    setShowProjectModal(false);
    setNewProjectName('');
    setNewProjectColor('#03a9f4');
  };

  const selectedProjectData = mockProjectsForTimer.find(p => p.id === selectedProject);

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>
      {/* Horizontal Timer Interface - Like Clockify */}
      <div className="flex items-center gap-4 w-full">
        {/* Description Input - Takes most space */}
        <div className="flex-1 min-w-0">
          <Input
            placeholder="What are you working on?"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="text-base border-gray-300 focus:border-primary focus:ring-1 focus:ring-primary h-10"
          />
        </div>

        {/* Project Selector */}
        <div className="w-60 min-w-60">
          <Select value={selectedProject} onValueChange={(value) => {
            setSelectedProject(value);
            const fullProject = getProjectById(value);
            setCurrentProject(fullProject || null);
          }}>
            <SelectTrigger className="border-gray-300 focus:border-primary focus:ring-1 focus:ring-primary h-10">
              <div className="flex items-center gap-2">
                {selectedProjectData ? (
                  <>
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: selectedProjectData.color }}
                    />
                    <FolderOpen className="w-4 h-4 text-gray-500" />
                    <span className="text-sm truncate">{selectedProjectData.name}</span>
                  </>
                ) : (
                  <>
                    <FolderOpen className="w-4 h-4 text-gray-500" />
                    <SelectValue placeholder="Project" />
                  </>
                )}
              </div>
            </SelectTrigger>
            <SelectContent>
              {mockProjectsForTimer.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: project.color }}
                    />
                    <span>{project.name}</span>
                    {project.client && (
                      <span className="text-xs text-gray-500">• {project.client}</span>
                    )}
                  </div>
                </SelectItem>
              ))}
              <Dialog open={showProjectModal} onOpenChange={setShowProjectModal}>
                <DialogTrigger asChild>
                  <div className="flex items-center gap-2 p-2 hover:bg-gray-50 cursor-pointer text-primary">
                    <Plus className="w-4 h-4" />
                    <span className="text-sm">Create new Project</span>
                  </div>
                </DialogTrigger>
              </Dialog>
            </SelectContent>
          </Select>
        </div>

        {/* Tags Button */}
        <Button variant="outline" size="sm" className="px-3 h-10">
          <Tag className="w-4 h-4" />
        </Button>

        {/* Timer Display */}
        <div className="text-xl font-mono font-bold text-gray-900 min-w-20 text-center">
          {formatTime(elapsedTime)}
        </div>

        {/* Start/Stop Button */}
        <Button
          onClick={handleStartStop}
          size="sm"
          className={`px-6 font-medium h-10 ${
            isActive
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-primary hover:bg-primary/90 text-primary-foreground'
          }`}
        >
          {isActive ? (
            <>
              <Square className="w-4 h-4 mr-1" />
              STOP
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-1" />
              START
            </>
          )}
        </Button>
      </div>

      {/* Status Bar */}
      {isActive && (
        <div className="flex items-center justify-between text-sm text-gray-600 bg-gray-50 rounded px-3 py-2 mt-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Timer running</span>
          </div>
          <span>Today</span>
        </div>
      )}

      {/* Create Project Modal */}
      <Dialog open={showProjectModal} onOpenChange={setShowProjectModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create new Project</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Input
                placeholder="Enter Project name"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                className="text-base"
              />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">Color:</span>
              <input
                type="color"
                value={newProjectColor}
                onChange={(e) => setNewProjectColor(e.target.value)}
                className="w-8 h-8 border border-gray-300 rounded cursor-pointer"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowProjectModal(false)}
              >
                Cancel
              </Button>
              <Button
                className="flex-1"
                onClick={handleCreateProject}
                disabled={!newProjectName.trim()}
              >
                CREATE
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Validation Modal */}
      <ValidationModal
        open={showValidationModal}
        onOpenChange={setShowValidationModal}
        validationErrors={validationErrors}
      />
    </div>
  );
}