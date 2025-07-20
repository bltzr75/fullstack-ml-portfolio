import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Todo, CreateTodoRequest, UpdateTodoRequest } from '../types/todo';
import { todoApi } from '../services/todoApi';

export type FilterType = 'all' | 'active' | 'completed';
export type SortType = 'created' | 'priority' | 'dueDate';

// Generate temporary ID for optimistic updates
const generateTempId = () => `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

interface TodoState {
  todos: Todo[];
  loading: boolean;
  error: string | null;
  filter: FilterType;
  sort: SortType;
  optimisticOperations: {
    [key: string]: 'creating' | 'updating' | 'deleting';
  };
}

const initialState: TodoState = {
  todos: [],
  loading: false,
  error: null,
  filter: 'all',
  sort: 'created',
  optimisticOperations: {},
};

// Async thunks (MVP Controllers)
export const fetchTodos = createAsyncThunk(
  'todos/fetchTodos',
  async () => {
    const todos = await todoApi.getAllTodos();
    return todos;
  }
);

export const createTodo = createAsyncThunk(
  'todos/createTodo',
  async (todoData: CreateTodoRequest, { dispatch, rejectWithValue }) => {
    const tempId = generateTempId();
    const now = new Date();
    
    // Optimistic update
    const optimisticTodo: Todo = {
      id: tempId,
      title: todoData.title,
      description: todoData.description,
      completed: false,
      priority: todoData.priority,
      dueDate: todoData.dueDate ? new Date(todoData.dueDate) : undefined,
      createdAt: now,
      updatedAt: now,
    };
    
    // Add optimistic todo
    dispatch(addTodoOptimistic(optimisticTodo));
    
    try {
      const newTodo = await todoApi.createTodo(todoData);
      return { tempId, newTodo };
    } catch (error) {
      // Remove optimistic todo on failure
      dispatch(removeOptimisticTodo(tempId));
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to create todo');
    }
  }
);

export const updateTodo = createAsyncThunk(
  'todos/updateTodo',
  async ({ id, todoData, originalTodo }: { id: string; todoData: UpdateTodoRequest; originalTodo: Todo }, { dispatch, rejectWithValue }) => {
    // Properly handle date conversion
    const updatedTodo: Todo = {
      ...originalTodo,
      // Handle each field explicitly to avoid type issues
      title: todoData.title !== undefined ? todoData.title : originalTodo.title,
      description: todoData.description !== undefined ? todoData.description : originalTodo.description,
      completed: todoData.completed !== undefined ? todoData.completed : originalTodo.completed,
      priority: todoData.priority !== undefined ? todoData.priority : originalTodo.priority,
      dueDate: todoData.dueDate !== undefined 
        ? (todoData.dueDate ? new Date(todoData.dueDate) : undefined)
        : originalTodo.dueDate,
      updatedAt: new Date(),
    };
    
    // Optimistic update
    dispatch(updateTodoOptimistic(updatedTodo));
    
    try {
      const serverTodo = await todoApi.updateTodo(id, todoData);
      return serverTodo;
    } catch (error) {
      // Rollback optimistic update
      dispatch(updateTodoOptimistic(originalTodo));
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to update todo');
    }
  }
);

export const deleteTodo = createAsyncThunk(
  'todos/deleteTodo',
  async (id: string, { dispatch, rejectWithValue }) => {
    // Mark as deleting
    dispatch(markTodoAsDeleting(id));
    
    try {
      await todoApi.deleteTodo(id);
      return id;
    } catch (error) {
      // Remove deleting mark
      dispatch(unmarkTodoAsDeleting(id));
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to delete todo');
    }
  }
);

export const toggleTodoComplete = createAsyncThunk(
  'todos/toggleTodoComplete',
  async (todo: Todo, { dispatch, rejectWithValue }) => {
    const updatedTodo: Todo = {
      ...todo,
      completed: !todo.completed,
      updatedAt: new Date(),
    };
    
    // Optimistic update
    dispatch(updateTodoOptimistic(updatedTodo));
    
    try {
      const serverTodo = await todoApi.updateTodo(todo.id, { completed: !todo.completed });
      return serverTodo;
    } catch (error) {
      // Rollback optimistic update
      dispatch(updateTodoOptimistic(todo));
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to update todo');
    }
  }
);

const todoSlice = createSlice({
  name: 'todos',
  initialState,
  reducers: {
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    
    // Optimistic operations
    addTodoOptimistic: (state, action: PayloadAction<Todo>) => {
      state.todos.push(action.payload);
      state.optimisticOperations[action.payload.id] = 'creating';
    },
    
    updateTodoOptimistic: (state, action: PayloadAction<Todo>) => {
      const index = state.todos.findIndex(todo => todo.id === action.payload.id);
      if (index !== -1) {
        state.todos[index] = action.payload;
        state.optimisticOperations[action.payload.id] = 'updating';
      }
    },
    
    markTodoAsDeleting: (state, action: PayloadAction<string>) => {
      state.optimisticOperations[action.payload] = 'deleting';
    },
    
    unmarkTodoAsDeleting: (state, action: PayloadAction<string>) => {
      delete state.optimisticOperations[action.payload];
    },
    
    removeOptimisticTodo: (state, action: PayloadAction<string>) => {
      state.todos = state.todos.filter(todo => todo.id !== action.payload);
      delete state.optimisticOperations[action.payload];
    },
    
    // Filter and sort
    setFilter: (state, action: PayloadAction<FilterType>) => {
      state.filter = action.payload;
    },
    setSort: (state, action: PayloadAction<SortType>) => {
      state.sort = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch todos
    builder
      .addCase(fetchTodos.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.loading = false;
        state.todos = action.payload;
      })
      .addCase(fetchTodos.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch todos';
      });
    
    // Create todo
    builder
      .addCase(createTodo.fulfilled, (state, action) => {
        const { tempId, newTodo } = action.payload;
        // Replace temp todo with real todo
        const index = state.todos.findIndex(todo => todo.id === tempId);
        if (index !== -1) {
          state.todos[index] = newTodo;
        }
        delete state.optimisticOperations[tempId];
      })
      .addCase(createTodo.rejected, (state, action) => {
        state.error = action.payload as string;
      });
    
    // Update todo
    builder
      .addCase(updateTodo.fulfilled, (state, action) => {
        const serverTodo = action.payload;
        const index = state.todos.findIndex(todo => todo.id === serverTodo.id);
        if (index !== -1) {
          state.todos[index] = serverTodo;
        }
        delete state.optimisticOperations[serverTodo.id];
      })
      .addCase(updateTodo.rejected, (state, action) => {
        state.error = action.payload as string;
      });
    
    // Delete todo
    builder
      .addCase(deleteTodo.fulfilled, (state, action) => {
        const todoId = action.payload;
        state.todos = state.todos.filter(todo => todo.id !== todoId);
        delete state.optimisticOperations[todoId];
      })
      .addCase(deleteTodo.rejected, (state, action) => {
        state.error = action.payload as string;
      });
    
    // Toggle complete
    builder
      .addCase(toggleTodoComplete.fulfilled, (state, action) => {
        const serverTodo = action.payload;
        const index = state.todos.findIndex(todo => todo.id === serverTodo.id);
        if (index !== -1) {
          state.todos[index] = serverTodo;
        }
        delete state.optimisticOperations[serverTodo.id];
      })
      .addCase(toggleTodoComplete.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const { 
  setError,
  addTodoOptimistic,
  updateTodoOptimistic,
  markTodoAsDeleting,
  unmarkTodoAsDeleting,
  removeOptimisticTodo,
  setFilter,
  setSort
} = todoSlice.actions;

export default todoSlice.reducer;
