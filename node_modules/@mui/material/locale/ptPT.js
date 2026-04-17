"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ptPT = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('pt-PT');
const ptPT = exports.ptPT = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: 'Mostrar caminho'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return 'Primeira página';
          }
          if (type === 'last') {
            return 'Última página';
          }
          if (type === 'next') {
            return 'Próxima página';
          }
          // if (type === 'previous') {
          return 'Página anterior';
        },
        labelRowsPerPage: 'Linhas por página:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)}–${formatNumber(to)} de ${count !== -1 ? formatNumber(count) : `mais de ${formatNumber(to)}`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => `${value} Estrela${value !== 1 ? 's' : ''}`,
        emptyLabelText: 'Vazio'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: 'Limpar',
        closeText: 'Fechar',
        loadingText: 'A carregar…',
        noOptionsText: 'Sem opções',
        openText: 'Abrir'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: 'Fechar'
      }
    },
    MuiPagination: {
      defaultProps: {
        'aria-label': 'Navegar por páginas',
        getItemAriaLabel: (type, page, selected) => {
          if (type === 'page') {
            return `${selected ? '' : 'Ir para a '}página ${page}`;
          }
          if (type === 'first') {
            return 'Primeira página';
          }
          if (type === 'last') {
            return 'Última página';
          }
          if (type === 'next') {
            return 'Próxima página';
          }
          // if (type === 'previous') {
          return 'Página anterior';
        }
      }
    }
  }
};