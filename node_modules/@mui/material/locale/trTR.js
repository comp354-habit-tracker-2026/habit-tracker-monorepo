"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.trTR = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('tr-TR');
const trTR = exports.trTR = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: 'Yolu göster'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return 'İlk sayfaya git';
          }
          if (type === 'last') {
            return 'Son sayfaya git';
          }
          if (type === 'next') {
            return 'Sonraki sayfaya git';
          }
          // if (type === 'previous') {
          return 'Önceki sayfaya git';
        },
        labelRowsPerPage: 'Sayfa başına satır:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)}-${formatNumber(to)} / ${count !== -1 ? formatNumber(count) : `${formatNumber(to)}'den fazla`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => `${value} Yıldız`,
        emptyLabelText: 'Boş'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: 'Temizle',
        closeText: 'Kapat',
        loadingText: 'Yükleniyor…',
        noOptionsText: 'Seçenek yok',
        openText: 'Aç'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: 'Kapat'
      }
    },
    MuiPagination: {
      defaultProps: {
        'aria-label': 'Sayfa navigasyonu',
        getItemAriaLabel: (type, page, selected) => {
          if (type === 'page') {
            return `${page}. ${selected ? 'sayfa' : 'sayfaya git'}`;
          }
          if (type === 'first') {
            return 'İlk sayfaya git';
          }
          if (type === 'last') {
            return 'Son sayfaya git';
          }
          if (type === 'next') {
            return 'Sonraki sayfaya git';
          }
          // if (type === 'previous') {
          return 'Önceki sayfaya git';
        }
      }
    }
  }
};