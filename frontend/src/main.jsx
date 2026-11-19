import { lazy } from 'react';
import './styles/app.css';
import { mountIslands } from './lib/islands';
import NavBar from './components/layout/NavBar';
import FaqAccordion from './components/faq/FaqAccordion';
import RotatingStatusIcons from './components/home/RotatingStatusIcons';
import FloatingBackground from './components/home/FloatingBackground';
import ContentBlock from './components/courses/ContentBlock';

export const registry = {
  NavBar,
  FaqAccordion,
  RotatingStatusIcons,
  FloatingBackground,
  ContentBlock,
  // the code editor (CodeMirror) is only downloaded on task pages
  TaskWorkspace: lazy(() => import('./components/task/TaskWorkspace')),
};

mountIslands(registry);
