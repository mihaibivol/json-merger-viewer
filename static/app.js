var app = angular.module('diffApp', ['ngSanitize']);

app.config(["$sanitizeProvider", function(sanitizeProvider) {
    sanitizeProvider.enableSvg();
}]);

app.directive('mergeView', function() {
    var controller = function($scope, $window, $sce) {
        $scope.mergeInfo = JSON.parse($scope.mergeInfoTxt);
        var jsondiffpatch = $window.jsondiffpatch;

        var format = function(delta, revision) {
            return $sce.trustAsHtml(
                jsondiffpatch.formatters.html.format(delta, revision));
        };
        var jsonDiff = jsondiffpatch.create({
            objectHash: function(obj, index) {
                if (obj._id !== undefined)
                    return obj._id;
                return '$$index' + index;
            },
            textDiff: {
                minLength: 60
            },
            propertyFilter: function(name) {
                return name !== '_id';
            },
            arrays: {
                detectMove: true,
                includeValueOnMove: true
            }
        });
        jsondiffpatch.formatters.html.showUnchanged();
        var same = '<h3>SAME</h3>';
        var rootHeadDiff = jsonDiff.diff($scope.mergeInfo.r_h_root,
                                         $scope.mergeInfo.r_h_head);
        var rootUpdateDiff = jsonDiff.diff($scope.mergeInfo.r_u_root,
                                           $scope.mergeInfo.r_u_update);
        var headMergedDiff = jsonDiff.diff($scope.mergeInfo.h_m_head,
                                           $scope.mergeInfo.h_m_merged);
        $scope.rootHeadDiff = format(rootHeadDiff,
                                     $scope.mergeInfo.r_h_root) || same;
        $scope.rootUpdateDiff = format(rootUpdateDiff,
                                       $scope.mergeInfo.r_u_root) || same;
        $scope.headMergedDiff = format(headMergedDiff,
                                       $scope.mergeInfo.h_m_head) || same;
    };

    return {
        'restrict': 'E',
        'scope': {
            'mergeInfoTxt': '@'
        },
        'controller': controller,
        'templateUrl': '/static/ng_templates/merge_view.html'
    };
});
