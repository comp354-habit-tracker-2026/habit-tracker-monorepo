"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.zhTW = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('zh-TW');
const zhTW = exports.zhTW = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: '展開'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return '第一頁';
          }
          if (type === 'last') {
            return '最後一頁';
          }
          if (type === 'next') {
            return '下一頁';
          }
          return '上一頁';
        },
        labelRowsPerPage: '每頁數量:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `${formatNumber(from)} ~ ${formatNumber(to)} / ${count !== -1 ? formatNumber(count) : `${formatNumber(to)} 以上`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => `${value} 顆星`,
        emptyLabelText: '無標籤'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: '清空',
        closeText: '關閉',
        loadingText: '載入中…',
        noOptionsText: '沒有可用選項',
        openText: '打開'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: '關閉'
      }
    }
  }
};