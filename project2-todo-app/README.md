# Project 2 - Todo List Application (NestJS + React)

A modern, full-stack todo application demonstrating production-ready development practices with optimistic updates, comprehensive state management, and Docker containerization.


**✅ All Core Requirements Met:**
- Full-stack application (NestJS + React + TypeScript)
- Complete CRUD operations with optimistic updates
- MVP architectural pattern with Redux Toolkit
- Material-UI responsive design
- Docker containerization with multi-stage builds
- Comprehensive error handling and validation
- In-memory storage with seed data for testing

## 🚀 Features

### **Core Functionality**
- ✅ **Create, Read, Update, Delete** todos with instant UI feedback
- ✅ **Optimistic Updates** - Changes appear immediately, rollback on errors
- ✅ **Mark todos as complete/incomplete** with real-time toggle
- ✅ **Inline editing** - Click edit button to modify todos directly
- ✅ **Delete confirmation** - Safe deletion with confirmation dialogs
- ✅ **Priority levels** - Low, Medium, High with color coding
- ✅ **Due dates** - Optional date picker with visual indicators
- ✅ **Seed data** - 5 sample todos loaded automatically for testing

### **Advanced Features**
- ✅ **Smart Filtering** - View All, Active, or Completed todos
- ✅ **Multiple Sorting** - By creation date, priority, or due date
- ✅ **Real-time Statistics** - Live counts of total, active, completed todos
- ✅ **Loading States** - Visual feedback during operations
- ✅ **Error Handling** - Graceful error messages and rollback mechanisms
- ✅ **Responsive Design** - Mobile-friendly Material-UI components

### **Technical Features**
- ✅ **MVP Architecture** - Clean separation of concerns
- ✅ **TypeScript** - Full type safety throughout the application
- ✅ **Redux Toolkit** - Modern state management with createAsyncThunk
- ✅ **Input Validation** - Backend validation with class-validator
- ✅ **Docker Ready** - Production and development containerization
- ✅ **CORS Configured** - Proper cross-origin resource sharing

## 🏗️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | NestJS + TypeScript | RESTful API with dependency injection |
| **Frontend** | React 18 + TypeScript | Modern reactive UI components |
| **UI Library** | Material-UI (MUI) | Professional, accessible components |
| **State Management** | Redux Toolkit | Predictable state with optimistic updates |
| **Validation** | class-validator | Backend input validation and sanitization |
| **Containerization** | Docker + Docker Compose | Development and production deployment |
| **Architecture** | MVP Pattern | Model-View-Presenter for clean separation |

## 🐳 Running the Application (Recommended)

### **Production Mode (Docker)**
```bash
cd project2-todo-app

# Build and start both services
sudo docker-compose up --build

# Or run in background
sudo docker-compose up -d --build
```

### **Development Mode (Docker with Hot Reload)**
```bash
cd project2-todo-app

# Start development environment with file watching
sudo docker-compose -f docker-compose.dev.yml up --build
```

### **Access the Application**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:3001
- **Health Check:** http://localhost:3001/todos

### **Stop Services**
```bash
# Stop containers
sudo docker-compose down

# Clean up (optional)
sudo docker system prune -f
```

## 💻 Local Development (Alternative)

### **Backend (Terminal 1)**
```bash
cd backend
npm install
npm run start:dev
```

### **Frontend (Terminal 2)**
```bash
cd frontend
npm install
npm start
```

## 📡 API Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/todos` | List all todos | - |
| `POST` | `/todos` | Create new todo | `CreateTodoDto` |
| `GET` | `/todos/:id` | Get single todo | - |
| `PUT` | `/todos/:id` | Update todo | `UpdateTodoDto` |
| `DELETE` | `/todos/:id` | Delete todo | - |

### **Data Models**

```typescript
interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

interface CreateTodoDto {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
}
```

## 🏛️ Architecture & Patterns

### **MVP (Model-View-Presenter) Pattern**
- **Model:** Redux store state and Todo entities
- **View:** React components (pure presentation)
- **Presenter:** Redux Toolkit async thunks (business logic controllers)

### **Optimistic Updates Flow**
1. User performs action (create/update/delete)
2. UI updates immediately (optimistic)
3. API request sent to backend
4. On success: confirm optimistic update
5. On failure: rollback UI to previous state + show error

### **Component Architecture**
```
TodoList (Container)
├── TodoForm (Create todos)
├── TodoFilters (Filter & sort controls)
└── TodoItem[] (Individual todo management)
    ├── Edit mode (inline editing)
    └── Delete confirmation dialog
```

## 📁 Project Structure

```
project2-todo-app/
├── 🐳 docker-compose.yml           # Production orchestration
├── 🐳 docker-compose.dev.yml       # Development with hot reload
├── 📖 README.md                    # This documentation
│
├── 🧱 backend/                     # NestJS API Server
│   ├── 🐳 Dockerfile               # Multi-stage production build
│   ├── 📦 package.json             # Dependencies & scripts
│   ├── ⚙️  tsconfig.json           # TypeScript configuration
│   └── 📂 src/
│       ├── 📁 todos/               # Todo module (feature-based)
│       │   ├── 📝 dto/             # Data Transfer Objects
│       │   │   ├── create-todo.dto.ts
│       │   │   └── update-todo.dto.ts
│       │   ├── 🎯 todo.entity.ts   # Todo interface/model
│       │   ├── 🎮 todo.controller.ts # HTTP request handlers
│       │   ├── 🔧 todo.service.ts  # Business logic & data
│       │   └── 📦 todo.module.ts   # NestJS module definition
│       ├── 🏠 app.module.ts        # Root application module
│       └── 🚀 main.ts              # Application entry point
│
└── 🎨 frontend/                    # React SPA Client
    ├── 🐳 Dockerfile               # Multi-stage production build
    ├── 🐳 Dockerfile.dev           # Development container
    ├── 📦 package.json             # Dependencies & scripts
    ├── ⚙️  tsconfig.json           # TypeScript configuration
    └── 📂 src/
        ├── 🧩 components/          # Reusable UI components
        │   ├── TodoList.tsx        # Main container component
        │   ├── TodoForm.tsx        # Todo creation form
        │   ├── TodoItem.tsx        # Individual todo display/edit
        │   └── TodoFilters.tsx     # Filtering & sorting controls
        ├── 🏪 store/               # Redux state management
        │   ├── store.ts            # Configure Redux store
        │   └── todoSlice.ts        # Todo state + async thunks
        ├── 🌐 services/            # API communication layer
        │   └── todoApi.ts          # HTTP client for backend
        ├── 📋 types/               # TypeScript type definitions
        │   └── todo.ts             # Shared interfaces
        ├── 🛠️  utils/              # Helper functions
        │   └── todoUtils.ts        # Filtering & sorting logic
        └── 🏠 App.tsx              # Root React component
```

## 🎬 Demo Features to Test

### **1. Seed Data**
- Application loads with 5 sample todos automatically
- Different priorities, completion states, and due dates
- Demonstrates all features immediately

### **2. Optimistic Updates**
- Create a todo → appears instantly, form clears
- Toggle completion → checkbox responds immediately
- Edit todo → changes show instantly when saved
- Delete todo → disappears immediately after confirmation

### **3. Filtering & Sorting**
- Filter by: All / Active / Completed
- Sort by: Creation Date / Priority / Due Date
- Real-time statistics update with filters

### **4. Error Handling**
- Stop backend container to test error states
- Watch rollback behavior and error messages
- UI gracefully handles API failures

### **5. Responsive Design**
- Works on desktop, tablet, and mobile
- Material-UI components adapt to screen size
- Touch-friendly interfaces

## 🔧 Development Features

### **Backend Development**
- Hot reload with `npm run start:dev`
- Input validation with decorators
- Structured error responses
- Comprehensive logging
- Memory-based storage (no database setup needed)

### **Frontend Development**
- Hot reload with React development server
- Redux DevTools integration
- TypeScript strict mode
- ESLint and Prettier configured
- Component-based architecture

### **Docker Development**
- Separate dev/prod configurations
- Volume mounting for hot reload
- Multi-stage builds for optimization
- Health checks and restart policies


### **Required Features ✅**
- [x] **Full-stack application** (NestJS + React)
- [x] **All CRUD operations** with proper HTTP methods
- [x] **Complete Todo model** with all required fields
- [x] **Material-UI components** used consistently
- [x] **Redux state management** with modern patterns
- [x] **MVP design pattern** implemented with thunks
- [x] **Optimistic updates** for immediate UI feedback
- [x] **Docker setup** with multi-stage builds
- [x] **Environment configuration** for dev/prod
- [x] **TypeScript throughout** both frontend and backend

### **Bonus Features ✅**
- [x] **Input validation** with class-validator
- [x] **Error handling** with proper HTTP status codes
- [x] **Loading states** and comprehensive error handling
- [x] **Seed data** for immediate testing
- [x] **Filtering and sorting** capabilities
- [x] **Statistics dashboard** with real-time counts
- [x] **Responsive design** that works on all devices

## 🚀 Next Steps

This application demonstrates production-ready development practices and can be extended with:

- **Database Integration:** PostgreSQL or MongoDB
- **Authentication:** JWT-based user sessions
- **Real-time Updates:** WebSocket synchronization
- **API Documentation:** Swagger/OpenAPI integration
- **Testing:** Unit and integration test suites
- **CI/CD:** Automated deployment pipelines
- **Monitoring:** Health checks and performance metrics

---

**Built with ❤️ using modern development practices and industry-standard tools.**
