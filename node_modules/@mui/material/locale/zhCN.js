"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.zhCN = void 0;
var _buildFormatNumber = _interopRequireDefault(require("./utils/buildFormatNumber"));
const formatNumber = (0, _buildFormatNumber.default)('zh-CN');
const zhCN = exports.zhCN = {
  components: {
    MuiBreadcrumbs: {
      defaultProps: {
        expandText: '展开'
      }
    },
    MuiTablePagination: {
      defaultProps: {
        getItemAriaLabel: type => {
          if (type === 'first') {
            return '第一页';
          }
          if (type === 'last') {
            return '最后一页';
          }
          if (type === 'next') {
            return '下一页';
          }
          return '上一页';
        },
        labelRowsPerPage: '每页行数:',
        labelDisplayedRows: ({
          from,
          to,
          count
        }) => `第 ${formatNumber(from)} 条到第 ${formatNumber(to)} 条，${count !== -1 ? `共 ${formatNumber(count)} 条` : `至少 ${formatNumber(to)} 条`}`
      }
    },
    MuiRating: {
      defaultProps: {
        getLabelText: value => `${value} 颗星`,
        emptyLabelText: '无标签'
      }
    },
    MuiAutocomplete: {
      defaultProps: {
        clearText: '清空',
        closeText: '关闭',
        loadingText: '加载中……',
        noOptionsText: '没有可用选项',
        openText: '打开'
      }
    },
    MuiAlert: {
      defaultProps: {
        closeText: '关闭'
      }
    }
  }
};