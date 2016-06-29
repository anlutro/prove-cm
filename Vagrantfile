#!/usr/bin/env ruby

Vagrant.configure(2) do |config|
	config.vm.box = 'box-cutter/debian82'
	config.vm.hostname = 'prove-test.vagrant.local'
	config.vm.network 'private_network', ip: '10.90.10.10'

	config.vm.synced_folder '.', '/vagrant', type: 'nfs'

	config.vm.provider :virtualbox do |vb|
		vb.customize ['modifyvm', :id, '--memory', '768']
		vb.customize ['modifyvm', :id, '--cpus', '1']
		vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
		vb.customize ['modifyvm', :id, '--natdnsproxy1', 'on']
		vb.customize ['guestproperty', 'set', :id, '/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold', 60000]
	end
end