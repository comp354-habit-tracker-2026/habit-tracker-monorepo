"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.nnNO = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('nn-NO');
const nnNO = exports.nnNO = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: 'Vis sti'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return 'Gå til første side';
          }
          if (type === 'last') {
            return 'Gå til siste side';
          }
          if (type === 'next') {
            return 'Gå til neste side';
          }
          // if (type === 'previous') {
          return 'Gå til førre side';
        },
        labelRowsPerPage: 'Rader per side:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)}–${formatNumber(to)} av ${count !== -1 ? formatNumber(count) : `fleire enn ${formatNumber(to)}`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => `${value} stjerne${value !== 1 ? 'r' : ''}`,
        emptyLabelText: 'Tom'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: 'Tøm',
        closeText: 'Lukk',
        loadingText: 'Lastar inn…',
        noOptionsText: 'Ingen alternativ',
        openText: 'Opna'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: 'Lukk'
      }
    },
    MuiPagination: {
      defaultProps: {
        'aria-label': 'Navigasjon for paginering',
        getItemAriaLabel: (type, page, selected) => {
          if (type === 'page') {
            return `${selected ? '' : 'Gå til '}side ${page}`;
          }
          if (type === 'first') {
            return 'Gå til første side';
          }
          if (type === 'last') {
            return 'Gå til siste side';
          }
          if (type === 'next') {
            return 'Gå til neste side';
          }
          // if (type === 'previous') {
          return 'Gå til førre side';
        }
      }
    }
  }
};