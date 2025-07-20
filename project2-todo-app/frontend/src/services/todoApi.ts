import { Todo, CreateTodoRequest, UpdateTodoRequest } from '../types/todo';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

export const todoApi = {
  // Get all todos
  getAllTodos: async (): Promise<Todo[]> => {
    const response = await fetch(`${API_BASE_URL}/todos`);
    if (!response.ok) {
      throw new Error('Failed to fetch todos');
    }
    return response.json();
  },

  // Create todo
  createTodo: async (todo: CreateTodoRequest): Promise<Todo> => {
    const response = await fetch(`${API_BASE_URL}/todos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(todo),
    });
    if (!response.ok) {
      throw new Error('Failed to create todo');
    }
    return response.json();
  },

  // Update todo
  updateTodo: async (id: string, todo: UpdateTodoRequest): Promise<Todo> => {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(todo),
    });
    if (!response.ok) {
      throw new Error('Failed to update todo');
    }
    return response.json();
  },

  // Delete todo
  deleteTodo: async (id: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete todo');
    }
  },
};
