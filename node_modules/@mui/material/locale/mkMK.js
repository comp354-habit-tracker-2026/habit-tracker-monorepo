"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.mkMK = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('mk-MK');

// Macedonian - Македонски
const mkMK = exports.mkMK = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: 'Прикажи патека'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return 'Оди на прва страница';
          }
          if (type === 'last') {
            return 'Оди на последна страница';
          }
          if (type === 'next') {
            return 'Оди на следна страница';
          }
          // if (type === 'previous') {
          return 'Оди на предходна страница';
        },
        labelRowsPerPage: 'Редови по страница:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)}–${formatNumber(to)} од ${count !== -1 ? formatNumber(count) : `повеќе од ${formatNumber(to)}`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => {
          const lastDigit = value % 10;
          return `${value} Ѕвезд${lastDigit === 1 ? 'а' : 'и'}`;
        },
        emptyLabelText: 'Празно'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: 'Избриши',
        closeText: 'Затвори',
        loadingText: 'Се презема',
        noOptionsText: 'Нема опција',
        openText: 'Отвори'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: 'Затвори'
      }
    },
    MuiPagination: {
      defaultProps: {
        'aria-label': 'Навигација низ страници',
        getItemAriaLabel: (type, page, selected) => {
          if (type === 'page') {
            return `${selected ? '' : 'Оди на '}страница ${page}`;
          }
          if (type === 'first') {
            return 'Оди на прва страница';
          }
          if (type === 'last') {
            return 'Оди на последна страница';
          }
          if (type === 'next') {
            return 'Оди на следна страница';
          }
          // if (type === 'previous') {
          return 'Оди на предходна страница';
        }
      }
    }
  }
};