import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { TodoService } from './todos/todo.service';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Initialize seed data
  const todoService = app.get(TodoService);
  todoService.initializeSeedData();
  
  // Enable CORS for frontend
  app.enableCors({
    origin: process.env.NODE_ENV === 'production' 
      ? ['http://localhost:3000', 'http://frontend:3000']
      : ['http://localhost:3000'],
    credentials: true,
  });
  
  const port = process.env.PORT || 3001;
  await app.listen(port);
  console.log(`Backend running on http://localhost:${port}`);
}
bootstrap();
