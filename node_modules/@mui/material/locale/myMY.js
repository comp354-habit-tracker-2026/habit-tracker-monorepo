"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.myMY = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('my-MY');

// Myanmar - မြန်မာ
const myMY = exports.myMY = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: 'လမ်းကြောင်းပြပါ။'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return 'ပထမစာမျက်နှာသို့သွားပါ။';
          }
          if (type === 'last') {
            return 'နောက်ဆုံးစာမျက်နှာသို့သွားပါ။';
          }
          if (type === 'next') {
            return 'နောက်စာမျက်နှာသို့သွားပါ။';
          }
          // if (type === 'previous') {
          return 'ယခင်စာမျက်နှာသို့သွားပါ။';
        },
        labelRowsPerPage: 'စာမျက်နှာအလိုက် အတန်းများ:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)}–${formatNumber(to)} ၏ ${count !== -1 ? formatNumber(count) : `ထက်ပိုပြီး ${formatNumber(to)}`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => {
          const lastDigit = value % 10;
          return `${value} ကြယ်ပွင့်${lastDigit === 1 ? '၎' : ''}`;
        },
        emptyLabelText: 'ဗလာ'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: 'ရှင်းလင်းသော',
        closeText: 'ပိတ်လိုက်',
        loadingText: 'ဖွင့်နေသည်…',
        noOptionsText: 'ရွေးချယ်ခွင့်မရှိပါ။',
        openText: 'ဖွင့်သည်။'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: 'ပိတ်လိုက်'
      }
    },
    MuiPagination: {
      defaultProps: {
        'aria-label': 'Pagination အညွှန်း',
        getItemAriaLabel: (type, page, selected) => {
          if (type === 'page') {
            return `${selected ? '' : 'သွားပါ။ '}စာမျက်နှာ ${page}`;
          }
          if (type === 'first') {
            return 'ပထမစာမျက်နှာသို့သွားပါ။';
          }
          if (type === 'last') {
            return 'နောက်ဆုံးစာမျက်နှာသို့သွားပါ။';
          }
          if (type === 'next') {
            return 'နောက်စာမျက်နှာသို့သွားပါ။';
          }
          // if (type === 'previous') {
          return 'ယခင်စာမျက်နှာသို့သွားပါ။';
        }
      }
    }
  }
};