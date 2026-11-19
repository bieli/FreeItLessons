// Django admin: statistics chart above the ContentStatus change list.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/admin.css';
import StatusPieChart, { countStatuses } from './components/admin/StatusPieChart';

const changelist = document.getElementById('changelist');
if (changelist) {
  const container = document.createElement('div');
  container.id = 'chart';
  changelist.parentNode.insertBefore(container, changelist);
  createRoot(container).render(
    <StrictMode>
      <StatusPieChart counts={countStatuses()} />
    </StrictMode>,
  );
}
