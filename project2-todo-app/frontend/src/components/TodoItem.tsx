import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  ListItem,
  ListItemText,
  Checkbox,
  IconButton,
  Typography,
  Chip,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Edit, Delete, Save, Cancel } from '@mui/icons-material';
import { Todo, UpdateTodoRequest } from '../types/todo';
import { RootState, AppDispatch } from '../store/store';
import { updateTodo, deleteTodo, toggleTodoComplete, setError } from '../store/todoSlice';

interface TodoItemProps {
  todo: Todo;
}

const TodoItem: React.FC<TodoItemProps> = ({ todo }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { optimisticOperations } = useSelector((state: RootState) => state.todos);
  const [isEditing, setIsEditing] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [editData, setEditData] = useState<UpdateTodoRequest>({
    title: todo.title,
    description: todo.description,
    priority: todo.priority,
    dueDate: todo.dueDate ? new Date(todo.dueDate).toISOString().split('T')[0] : '',
  });

  const isBeingDeleted = optimisticOperations[todo.id] === 'deleting';
  const isBeingUpdated = optimisticOperations[todo.id] === 'updating';
  const isBeingCreated = optimisticOperations[todo.id] === 'creating';

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleToggleComplete = async () => {
    setLoading(true);
    try {
      await dispatch(toggleTodoComplete(todo));
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditData({
      title: todo.title,
      description: todo.description,
      priority: todo.priority,
      dueDate: todo.dueDate ? new Date(todo.dueDate).toISOString().split('T')[0] : '',
    });
  };

  const handleSaveEdit = async () => {
    if (!editData.title?.trim()) {
      dispatch(setError('Title is required'));
      return;
    }

    setLoading(true);
    try {
      await dispatch(updateTodo({
        id: todo.id,
        todoData: {
          ...editData,
          description: editData.description || undefined,
          dueDate: editData.dueDate || undefined,
        },
        originalTodo: todo
      }));
      setIsEditing(false);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await dispatch(deleteTodo(todo.id));
      setDeleteDialogOpen(false);
    } finally {
      setLoading(false);
    }
  };

  const handleEditChange = (field: keyof UpdateTodoRequest) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | any
  ) => {
    setEditData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  // Don't render if being deleted (optimistic update)
  if (isBeingDeleted) {
    return null;
  }

  if (isEditing) {
    return (
      <ListItem divider>
        <Box sx={{ width: '100%', opacity: isBeingUpdated ? 0.7 : 1 }}>
          <TextField
            fullWidth
            value={editData.title}
            onChange={handleEditChange('title')}
            margin="normal"
            size="small"
            disabled={loading || isBeingUpdated}
            label="Title"
          />
          <TextField
            fullWidth
            value={editData.description}
            onChange={handleEditChange('description')}
            multiline
            rows={2}
            margin="normal"
            size="small"
            disabled={loading || isBeingUpdated}
            label="Description"
          />
          <FormControl fullWidth margin="normal" size="small" disabled={loading || isBeingUpdated}>
            <InputLabel>Priority</InputLabel>
            <Select
              value={editData.priority}
              label="Priority"
              onChange={handleEditChange('priority')}
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            type="date"
            value={editData.dueDate}
            onChange={handleEditChange('dueDate')}
            margin="normal"
            size="small"
            disabled={loading || isBeingUpdated}
            label="Due Date"
            InputLabelProps={{
              shrink: true,
            }}
          />
          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            <IconButton 
              onClick={handleSaveEdit} 
              disabled={loading || isBeingUpdated} 
              color="primary"
            >
              <Save />
            </IconButton>
            <IconButton 
              onClick={handleCancelEdit} 
              disabled={loading || isBeingUpdated}
            >
              <Cancel />
            </IconButton>
          </Box>
        </Box>
      </ListItem>
    );
  }

  return (
    <>
      <ListItem 
        divider 
        sx={{ 
          opacity: isBeingUpdated || isBeingCreated ? 0.7 : 1,
          transition: 'opacity 0.2s ease-in-out'
        }}
      >
        <Checkbox
          checked={todo.completed}
          onChange={handleToggleComplete}
          disabled={loading || isBeingUpdated}
        />
        <ListItemText
          primary={
            <Typography 
              variant="h6" 
              component="div"
              sx={{ 
                textDecoration: todo.completed ? 'line-through' : 'none',
                color: todo.completed ? 'text.secondary' : 'text.primary'
              }}
            >
              {todo.title}
              {isBeingCreated && (
                <Chip 
                  label="Creating..." 
                  size="small" 
                  sx={{ ml: 1 }}
                  color="info"
                />
              )}
            </Typography>
          }
          secondary={
            <div>
              {todo.description && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {todo.description}
                </Typography>
              )}
              <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                <Chip 
                  label={todo.priority} 
                  color={getPriorityColor(todo.priority) as any}
                  size="small"
                />
                <Chip 
                  label={todo.completed ? 'Completed' : 'Active'} 
                  color={todo.completed ? 'success' : 'primary'}
                  size="small"
                  variant="outlined"
                />
                {todo.dueDate && (
                  <Chip 
                    label={`Due: ${formatDate(todo.dueDate.toString())}`}
                    size="small"
                    variant="outlined"
                  />
                )}
              </div>
            </div>
          }
        />
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton 
            onClick={handleEdit} 
            disabled={loading || isBeingUpdated || isBeingCreated}
          >
            <Edit />
          </IconButton>
          <IconButton 
            onClick={() => setDeleteDialogOpen(true)} 
            disabled={loading || isBeingUpdated || isBeingCreated} 
            color="error"
          >
            <Delete />
          </IconButton>
        </Box>
      </ListItem>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Todo</DialogTitle>
        <DialogContent>
          Are you sure you want to delete "{todo.title}"?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" disabled={loading}>
            {loading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default TodoItem;
