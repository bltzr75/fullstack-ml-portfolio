import { Injectable, NotFoundException } from '@nestjs/common';
import { Todo } from './todo.entity';
import { CreateTodoDto } from './dto/create-todo.dto';
import { UpdateTodoDto } from './dto/update-todo.dto';

@Injectable()
export class TodoService {
  private todos: Todo[] = [];
  private idCounter = 1;

  /**
   * Initialize the service with seed data for testing
   */
  initializeSeedData(): void {
    if (this.todos.length === 0) {
      const now = new Date();
      const seedTodos: Todo[] = [
        {
          id: '1',
          title: 'Welcome to your Todo App! 🎉',
          description: 'This is your first todo item. You can edit, complete, or delete it. Try clicking the edit button to modify this todo.',
          completed: false,
          priority: 'medium',
          dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
          createdAt: now,
          updatedAt: now,
        },
        {
          id: '2',
          title: 'Try the filtering options',
          description: 'Use the filter buttons above to view all, active, or completed todos. This helps you organize and focus on what needs to be done.',
          completed: false,
          priority: 'high',
          dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), // 3 days from now
          createdAt: new Date(now.getTime() - 60 * 60 * 1000), // 1 hour ago
          updatedAt: new Date(now.getTime() - 60 * 60 * 1000),
        },
        {
          id: '3',
          title: 'Test the sorting features',
          description: 'Sort todos by priority, due date, or creation date using the dropdown menu. This example is already completed to show you the different states.',
          completed: true,
          priority: 'low',
          dueDate: undefined,
          createdAt: new Date(now.getTime() - 2 * 60 * 60 * 1000), // 2 hours ago
          updatedAt: new Date(now.getTime() - 30 * 60 * 1000), // 30 minutes ago
        },
        {
          id: '4',
          title: 'Create your own todos',
          description: 'Use the form above to create new todos. You can set priority levels, due dates, and descriptions.',
          completed: false,
          priority: 'medium',
          dueDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000), // 1 day from now
          createdAt: new Date(now.getTime() - 3 * 60 * 60 * 1000), // 3 hours ago
          updatedAt: new Date(now.getTime() - 3 * 60 * 60 * 1000),
        },
        {
          id: '5',
          title: 'Mark this todo as complete',
          description: 'Click the checkbox next to this todo to mark it as completed and see how the UI changes.',
          completed: false,
          priority: 'high',
          dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // 2 days from now
          createdAt: new Date(now.getTime() - 4 * 60 * 60 * 1000), // 4 hours ago
          updatedAt: new Date(now.getTime() - 4 * 60 * 60 * 1000),
        },
      ];
      
      this.todos = seedTodos;
      this.idCounter = 6; // Start from 6 for new todos
      
      console.log('✅ Initialized todo service with seed data:', this.todos.length, 'todos');
    } else {
      console.log('📝 Todo service already has data:', this.todos.length, 'todos');
    }
  }

  /**
   * Get all todos
   */
  findAll(): Todo[] {
    return this.todos;
  }

  /**
   * Get a single todo by ID
   */
  findOne(id: string): Todo {
    const todo = this.todos.find(t => t.id === id);
    if (!todo) {
      throw new NotFoundException(`Todo with ID ${id} not found`);
    }
    return todo;
  }

  /**
   * Create a new todo
   */
  create(createTodoDto: CreateTodoDto): Todo {
    const now = new Date();
    const todo: Todo = {
      id: this.idCounter.toString(),
      title: createTodoDto.title,
      description: createTodoDto.description,
      completed: false,
      priority: createTodoDto.priority,
      dueDate: createTodoDto.dueDate ? new Date(createTodoDto.dueDate) : undefined,
      createdAt: now,
      updatedAt: now,
    };
    
    this.idCounter++;
    this.todos.push(todo);
    
    console.log('📝 Created new todo:', todo.id, '-', todo.title);
    return todo;
  }

  /**
   * Update an existing todo
   */
  update(id: string, updateTodoDto: UpdateTodoDto): Todo {
    const todo = this.findOne(id);
    
    // Update only provided fields
    if (updateTodoDto.title !== undefined) {
      todo.title = updateTodoDto.title;
    }
    if (updateTodoDto.description !== undefined) {
      todo.description = updateTodoDto.description;
    }
    if (updateTodoDto.completed !== undefined) {
      todo.completed = updateTodoDto.completed;
    }
    if (updateTodoDto.priority !== undefined) {
      todo.priority = updateTodoDto.priority;
    }
    if (updateTodoDto.dueDate !== undefined) {
      todo.dueDate = updateTodoDto.dueDate ? new Date(updateTodoDto.dueDate) : undefined;
    }
    
    todo.updatedAt = new Date();
    
    console.log('📝 Updated todo:', todo.id, '-', todo.title);
    return todo;
  }

  /**
   * Delete a todo
   */
  remove(id: string): void {
    const index = this.todos.findIndex(t => t.id === id);
    if (index === -1) {
      throw new NotFoundException(`Todo with ID ${id} not found`);
    }
    
    const deletedTodo = this.todos[index];
    this.todos.splice(index, 1);
    
    console.log('🗑️ Deleted todo:', deletedTodo.id, '-', deletedTodo.title);
  }

  /**
   * Get statistics about todos
   */
  getStatistics() {
    const total = this.todos.length;
    const completed = this.todos.filter(todo => todo.completed).length;
    const active = total - completed;
    const byPriority = {
      high: this.todos.filter(todo => todo.priority === 'high').length,
      medium: this.todos.filter(todo => todo.priority === 'medium').length,
      low: this.todos.filter(todo => todo.priority === 'low').length,
    };
    
    return {
      total,
      completed,
      active,
      byPriority,
    };
  }

  /**
   * Clear all todos (useful for testing)
   */
  clearAll(): void {
    this.todos = [];
    this.idCounter = 1;
    console.log('🧹 Cleared all todos');
  }
}
