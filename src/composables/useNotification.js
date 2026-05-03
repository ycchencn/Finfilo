// composables/useNotification.js
import { useToast } from 'primevue/usetoast';

export function useNotification() {
  const toast = useToast();

  const showSuccess = (content) => {
    toast.add({ severity: 'success', summary: 'Success', detail: content, life: 3000 });
  };

  const showInfo = (content) => {
    toast.add({ severity: 'info', summary: 'Info', detail: content, life: 3000 });
  };

  const showError = (content) => {
    toast.add({ severity: 'error', summary: 'Error', detail: content, life: 3000 });
  };

  return {
    showSuccess,
    showInfo,
    showError
  };
}
