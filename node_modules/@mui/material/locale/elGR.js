"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.elGR = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('el-GR');
const elGR = exports.elGR = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: 'Εμφάνιση διαδρομής'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return 'Πρώτη σελίδα';
          }
          if (type === 'last') {
            return 'Τελευταία σελίδα';
          }
          if (type === 'next') {
            return 'Επόμενη σελίδα';
          }

          // if (type === "previous") {
          return 'Προηγούμενη σελίδα';
        },
        labelRowsPerPage: 'Γραμμές ανα σελίδα:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)}–${formatNumber(to)} από ${count !== -1 ? formatNumber(count) : `πάνω από ${formatNumber(to)}`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => `${value} Αστέρι${value !== 1 ? 'α' : ''}`,
        emptyLabelText: 'Χωρίς βαθμολόγηση'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: 'Καθαρισμός',
        closeText: 'Κλείσιμο',
        loadingText: 'Φόρτωση…',
        noOptionsText: 'Δεν υπάρχουν επιλογές',
        openText: 'Άνοιγμα'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: 'Κλείσιμο'
      }
    },
    MuiPagination: {
      defaultProps: {
        'aria-label': 'Πλοήγηση σε σελίδες',
        getItemAriaLabel: (type, page, selected) => {
          if (type === 'page') {
            return `${selected ? '' : 'Μετάβαση '}σελίδα ${page}`;
          }
          if (type === 'first') {
            return 'Πρώτη σελίδα';
          }
          if (type === 'last') {
            return 'Τελευταία σελίδα';
          }
          if (type === 'next') {
            return 'Επόμενη σελίδα';
          }

          // if (type === "previous") {
          return 'Προηγούμενη σελίδα';
        }
      }
    }
  }
};