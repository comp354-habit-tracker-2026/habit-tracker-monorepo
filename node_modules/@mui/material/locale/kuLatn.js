"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.kuLatn = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('ku-Latn');
const kuLatn = exports.kuLatn = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: 'Rê nîşan bide'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return 'Biçe rûpela yekem';
          }
          if (type === 'last') {
            return 'Biçe rûpela dawî';
          }
          if (type === 'next') {
            return 'Biçe rûpela din';
          }
          // if (type === 'previous') {
          return 'Biçe rûpela berê';
        },
        labelRowsPerPage: 'Rêz li ser rûpelê:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)}–${formatNumber(to)} of ${count !== -1 ? formatNumber(count) : `zêdetir ji ${formatNumber(to)}`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => `${value} Stêrk`,
        emptyLabelText: 'Vala'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: 'Paqij bike',
        closeText: 'Bigre',
        loadingText: 'Tê barkirin…',
        noOptionsText: 'Vebijêrk tune',
        openText: 'Veke'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: 'Bigre'
      }
    },
    MuiPagination: {
      defaultProps: {
        'aria-label': 'Navîgasyona rûpelan',
        getItemAriaLabel: (type, page, selected) => {
          if (type === 'page') {
            return `${selected ? '' : 'Biçe '}rûpel ${page}`;
          }
          if (type === 'first') {
            return 'Biçe rûpela yekem';
          }
          if (type === 'last') {
            return 'Biçe rûpela dawî';
          }
          if (type === 'next') {
            return 'Biçe rûpela din';
          }
          // if (type === 'previous') {
          return 'Biçe rûpela berê';
        }
      }
    }
  }
};