<template>
	<keep-alive include="RecorderDetail">
		<router-view/>
	</keep-alive>
</template>

<script>
export default {
	name: "RecorderRoot",
	watch: {
		$route() {
			finergy.router.current_route = finergy.router.parse();
			finergy.breadcrumbs.update();
		}
	}
};
</script>
