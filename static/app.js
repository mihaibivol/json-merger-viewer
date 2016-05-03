var app = angular.module('diffApp', ['ds.objectDiff']);

app.directive('mergeView', function() {
    var controller = function($scope, ObjectDiff) {
        $scope.rootHeadDiff = ObjectDiff.diff($scope.mergeInfo.root,
                                              $scope.mergeInfo.head)
        $scope.rootUpdateDiff = ObjectDiff.diff($scope.mergeInfo.root,
                                                $scope.mergeInfo.update)
        $scope.headMergedDiff = ObjectDiff.diff($scope.mergeInfo.head,
                                                $scope.mergeInfo.merged)
    };

    return {
        'restrict': 'E',
        'scope': {
            'mergeInfo': '='
        },
        'controller': controller,
        'templateUrl': '/static/ng_templates/merge_view.html'
    };
});
