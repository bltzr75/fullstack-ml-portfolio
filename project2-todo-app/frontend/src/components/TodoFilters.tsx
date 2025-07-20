import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Paper,
  Box,
  ButtonGroup,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Chip,
  Divider,
} from '@mui/material';
import { FilterAlt, Sort } from '@mui/icons-material';
import { RootState } from '../store/store';
import { setFilter, setSort, FilterType, SortType } from '../store/todoSlice';

const TodoFilters: React.FC = () => {
  const dispatch = useDispatch();
  const { todos, filter, sort } = useSelector((state: RootState) => state.todos);

  const handleFilterChange = (newFilter: FilterType) => {
    dispatch(setFilter(newFilter));
  };

  const handleSortChange = (event: any) => {
    dispatch(setSort(event.target.value as SortType));
  };

  // Calculate statistics
  const totalTodos = todos.length;
  const activeTodos = todos.filter(todo => !todo.completed).length;
  const completedTodos = todos.filter(todo => todo.completed).length;

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* Statistics */}
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
          <Typography variant="subtitle2" color="textSecondary">
            Statistics:
          </Typography>
          <Chip label={`Total: ${totalTodos}`} size="small" />
          <Chip label={`Active: ${activeTodos}`} size="small" color="primary" />
          <Chip label={`Completed: ${completedTodos}`} size="small" color="success" />
        </Box>

        <Divider />

        {/* Filters and Sort */}
        <Box sx={{ 
          display: 'flex', 
          gap: 2, 
          alignItems: 'center', 
          flexWrap: 'wrap',
          justifyContent: 'space-between'
        }}>
          {/* Filter Buttons */}
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <FilterAlt color="action" />
            <Typography variant="subtitle2" color="textSecondary">
              Filter:
            </Typography>
            <ButtonGroup size="small">
              <Button
                variant={filter === 'all' ? 'contained' : 'outlined'}
                onClick={() => handleFilterChange('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'active' ? 'contained' : 'outlined'}
                onClick={() => handleFilterChange('active')}
              >
                Active
              </Button>
              <Button
                variant={filter === 'completed' ? 'contained' : 'outlined'}
                onClick={() => handleFilterChange('completed')}
              >
                Completed
              </Button>
            </ButtonGroup>
          </Box>

          {/* Sort Dropdown */}
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Sort color="action" />
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Sort by</InputLabel>
              <Select
                value={sort}
                label="Sort by"
                onChange={handleSortChange}
              >
                <MenuItem value="created">Creation Date</MenuItem>
                <MenuItem value="priority">Priority</MenuItem>
                <MenuItem value="dueDate">Due Date</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default TodoFilters;
