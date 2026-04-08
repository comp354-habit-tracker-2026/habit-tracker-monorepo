import './confirm-dialog.css';

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDangerous?: boolean;
  isLoading?: boolean;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
}

/**
 * A simple confirmation dialog component.
 * Can be used for destructive actions like disconnecting accounts.
 */
export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDangerous = false,
  isLoading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="confirm-dialog-overlay"
      onClick={(e) => {
        // Only close if clicking outside the dialog
        if ((e.target as HTMLElement) === e.currentTarget) {
          onCancel();
        }
      }}
    >
      <div className="confirm-dialog">
        <h2 className="confirm-dialog__title">{title}</h2>
        <p className="confirm-dialog__message">{message}</p>
        <div className="confirm-dialog__actions">
          <button
            className="confirm-dialog__button confirm-dialog__button--cancel"
            onClick={onCancel}
            disabled={isLoading}
          >
            {cancelText}
          </button>
          <button
            className={`confirm-dialog__button confirm-dialog__button--confirm ${
              isDangerous ? 'confirm-dialog__button--dangerous' : ''
            }`}
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
